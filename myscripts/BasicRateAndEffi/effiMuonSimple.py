###############################################################
# Script to compute rates like the menu team did in 2022
# Directly over the tree: tree.GetEntries( SELECTION STRING )
###############################################################


#!/usr/bin/env python
from L1Trigger.Phase2L1GMTNtuples.format_histo import format_histo, format_histo2d
from L1Trigger.Phase2L1GMTNtuples.awkward_tools import merge_records, variable_collection, get_obj_dr
# from L1Trigger.Phase2L1GMTNtuples.awkward_tools import fill_th1_array as fill_th1, fill_th2_array as fill_th2
from L1Trigger.Phase2L1GMTNtuples.awkward_tools import fill_th1, fill_th2
from L1Trigger.Phase2L1GMTNtuples.yaml_cfg import Config
from ROOT import *
import math, sys, git, os, tqdm, numpy as np, uproot as ut, awkward as ak, vector
TH1.GetDefaultSumw2()


cfg = Config.from_file(f'{os.path.dirname(__file__)}/config/effi_gmt_tk_muon.yaml')
cfg.parse_args()

filename = f'{cfg.filepath}/{cfg.file}.root'
l1_tree = ut.lazy( f"{filename}:gmtTkMuonChecksTree/L1PhaseIITree" )
gen_tree = ut.lazy( f"{filename}:genTree/L1GenTree" )

tree = merge_records(l1_tree, gen_tree)
entries = len(tree)

TH1.GetDefaultSumw2()

print("=========================================================")
print("Computing Isolation Efficiencies from %s" % filename)
print("Total Events: %d" % entries)
print("Pt Range: %.0f - %.0f" % tuple(cfg.pt_range))
print("Eta Range: %.1f - %.1f" % tuple(cfg.eta_range))
print("=========================================================")

class namespace:
    def __init__(self, **kwargs):
        self._keys = list(kwargs.keys())
        self.__dict__.update(**kwargs)
    def keys(self): return self._keys
    def values(self): return ( getattr(self, key) for key in self._keys )
    def items(self):
        return ( (key, getattr(self, key)) for key in self._keys )

histos = namespace(
    genpt = format_histo("genMuonPt", "Gen Muon Pt", 20, 0, 100),
    geneta = format_histo("genMuonEta", "Gen Muon Eta", 50, -2.5, 2.5),
    gencount = format_histo("CountGenMuons", "CountGenPt20", 10, 0, 10),
    gen_2dpteta = format_histo2d(f"genMuon2DPtEta", "Gen Muon Pt vs Eta", 20, 0, 100, 50, -2.5, 2.5),

    bestdr = format_histo(f"bestDeltaR_{cfg.branch}_{cfg.label}","Best Delta R", 100, 0, 1),
    match_check = format_histo(f"matchCheck_{cfg.branch}_{cfg.label}", "", 10, 0 ,10),

    match_genpt = format_histo(f"matchGen_{cfg.branch}_{cfg.label}_Pt", cfg.label, 20, 0, 100),
    match_geneta = format_histo(f"matchGen_{cfg.branch}_{cfg.label}_Eta", cfg.label, 50, -2.5, 2.5),
    match_genphi = format_histo(f"matchGen_{cfg.branch}_{cfg.label}_Phi", cfg.label, 100, -4, 4),
    match_gen_2dpteta = format_histo2d(f"matchGen_{cfg.branch}_{cfg.label}_2DPtEta", cfg.label, 20, 0, 100, 50, -2.5, 2.5),

    unmatch_genpt = format_histo(f"noMatchGen_{cfg.branch}_{cfg.label}_Pt", cfg.label, 20, 0, 100),
    unmatch_geneta = format_histo(f"noMatchGen_{cfg.branch}_{cfg.label}_Eta", cfg.label, 50, -2.5, 2.5),
    unmatch_genphi = format_histo(f"noMatchGen_{cfg.branch}_{cfg.label}_Phi", cfg.label, 100, -4, 4),

    match_l1pt = format_histo(f"match_l1_{cfg.branch}_{cfg.label}_Pt", cfg.label, 20, 0, 100),
    match_l1eta = format_histo(f"match_l1_{cfg.branch}_{cfg.label}_Eta", cfg.label, 50, -2.5, 2.5),
    match_l1phi = format_histo(f"match_l1_{cfg.branch}_{cfg.label}_Phi", cfg.label, 100, -4, 4),

    match_l1ptres = format_histo(f"match_l1__{cfg.branch}_{cfg.label}_ptres","l1 pt - gen pt / gen pt", 100, -1, 1),

    effi_pt = format_histo(f"effi_{cfg.branch}_{cfg.label}_Pt", cfg.label, 20, 0, 100, color=kRed),
    effi_eta = format_histo(f"effi_{cfg.branch}_{cfg.label}_Eta", cfg.label, 50, -2.5, 2.5, color=kRed),
)

if cfg.total > 0:
    tree = tree[:cfg.total]

##############################
# Get Gen and L1 Particle Collections 
##############################

gen_parts = variable_collection(tree, 'part')
l1_parts = variable_collection(tree, cfg.branch)

##############################
# Make Gen particle selection 
##############################
print (" ... Masking Gen Particles")
gen_mask = [
    gen_parts.Stat == 1,
    abs(gen_parts.Id) == 13,
    abs(gen_parts.Eta) > cfg.eta_range[0],
    abs(gen_parts.Eta) < cfg.eta_range[1],
    gen_parts.Pt > cfg.pt_range[0],
    gen_parts.Pt < cfg.pt_range[1],
]
gen_mask = sum(gen_mask) == len(gen_mask)

gen_counts = ak.sum(gen_mask, axis=-1)
gen_parts = gen_parts[gen_mask]
gen_mask = gen_mask[gen_mask]

##############################
# Fill Gen particle values
##############################
print (" ... Filling Gen Particles")

fill_th1(histos.gencount, gen_counts)
fill_th1(histos.genpt, gen_parts.Pt)
fill_th1(histos.geneta, gen_parts.Eta)
fill_th2(histos.gen_2dpteta, gen_parts.Pt, gen_parts.Eta)

##############################
# Find nearest L1 particle in delta R to Gen particle
##############################
print (" ... Matching Gen Particles")

l1_delta_r = get_obj_dr(gen_parts, l1_parts[:, None])
matched_delta_r, matched_l1_index = ak.min(l1_delta_r, axis=2), ak.argmin(l1_delta_r, axis=2)
fill_th1(histos.bestdr, matched_delta_r)

print (" ... Matched Gen Particles")
matched_mask = matched_delta_r < cfg.matched_delta_r
matched_mask = ak.fill_none(matched_mask, False)

matched_gen = gen_parts[matched_mask]

##############################
# Fill matched Gen/L1 particle values
##############################
print (" ... Filling Matched Gen Particles")

matched_l1_pt = l1_parts.Pt[matched_l1_index][matched_mask]
matched_l1_eta = l1_parts.Eta[matched_l1_index][matched_mask]
matched_l1_phi = l1_parts.Phi[matched_l1_index][matched_mask]

ptres = (matched_l1_pt- matched_gen.Pt)/matched_gen.Pt
fill_th1(histos.match_check, matched_l1_index)
fill_th1(histos.match_genpt, matched_gen.Pt)
fill_th1(histos.match_geneta, matched_gen.Eta)
fill_th1(histos.match_genphi, matched_gen.Phi)
fill_th2(histos.match_gen_2dpteta, matched_gen.Pt, matched_gen.Eta)

fill_th1(histos.match_l1pt, matched_l1_pt)
fill_th1(histos.match_l1eta, matched_l1_eta)
fill_th1(histos.match_l1phi, matched_l1_phi)
fill_th1(histos.match_l1ptres, ptres)

##############################
# Fill unmatched Gen/L1 particle values
##############################
print (" ... Filling Unmatched Gen Particles")
unmatched_gen = gen_parts[~matched_mask]

fill_th1(histos.unmatch_genpt,  unmatched_gen.Pt)
fill_th1(histos.unmatch_geneta, unmatched_gen.Eta)
fill_th1(histos.unmatch_genphi, unmatched_gen.Phi)

# To compute the efficiency: ratio of gen muons matched to l1  over total of
# gen muons (using the binomial option B)
histos.effi_pt.Divide(histos.match_genpt, histos.genpt, 1, 1, "B")
histos.effi_eta.Divide(histos.match_geneta, histos.geneta, 1, 1, "B")

# SAVE OUTPUT
#################

outfile = cfg.outfile.format(file=cfg.file, label=cfg.label)

print(f"Saving  the efficiencies in {outfile}")

out = TFile(outfile, "RECREATE")
out.cd()

for key, histo in histos.items():
    histo.Write()
