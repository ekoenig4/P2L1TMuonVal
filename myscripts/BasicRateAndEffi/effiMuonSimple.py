###############################################################
###############################################################


#!/usr/bin/env python3
from typing import Any
from L1Trigger.Phase2L1GMTNtuples.root_tools import format_histo, format_histo2d, fill_th1, fill_th2
from L1Trigger.Phase2L1GMTNtuples.awkward_tools import cumand
from L1Trigger.Phase2L1GMTNtuples.hep_tools import get_dr, pair_opposite_charged_parts, pair_opposite_hw_charged_parts
from L1Trigger.Phase2L1GMTNtuples.yaml_cfg import Config
from ROOT import *
from collections import defaultdict
import math, sys, git, os, tqdm, numpy as np, uproot as ut, awkward as ak, vector
vector.register_awkward()
TH1.GetDefaultSumw2()


cfg = Config.from_file(f'{os.path.dirname(__file__)}/config/effi_gmt_tk_muon.yaml')
cfg.parse_args() # read all avaiable argparse variables from command line if given
cfg.replace() # replace all {} variables in config where available

cfg.pt_range = (cfg.pt_min, cfg.pt_max)
cfg.eta_range = (cfg.eta_min, cfg.eta_max)


filename = os.path.join(cfg.filepath,f'{cfg.file}.root')
gen_tree = ut.lazy( f"{filename}:genTree/L1GenTree" )
l1_tree = ut.lazy( f"{filename}:gmtTkMuonChecksTree/L1PhaseIITree" )

gen_entries = len(gen_tree)
l1_entries = len(l1_tree)

if l1_entries != gen_entries:
    raise ValueError()

entries = gen_entries

TH1.GetDefaultSumw2()

print("=========================================================")
print("Computing L1 Match Efficiencies from %s" % filename)
print("Total Events: %d" % entries)
print("Pt Range: %.0f - %.0f" % tuple(cfg.pt_range))
print("Eta Range: %.1f - %.1f" % tuple(cfg.eta_range))
print("=========================================================")

class namespace:
    def __init__(self, **kwargs):
        self._keys = list(kwargs.keys())
        self.__dict__.update(**kwargs)
    def __setitem__(self, key : str, value):
        self._keys.append(key)
        self.__dict__[key] = value
    def __getitem__(self, key : str): return self.__dict__[key]
    def keys(self): return self._keys
    def values(self): return ( getattr(self, key) for key in self._keys )
    def items(self):
        return ( (key, getattr(self, key)) for key in self._keys )

def format_pt_histo(name, title, bins=20, lo=0, hi=100, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_eta_histo(name, title, bins=50, lo=-2.5, hi=2.5, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_phi_histo(name, title, bins=100, lo=-4, hi=4, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_m_histo(name, title, bins=100, lo=20, hi=200, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_pteta_histo2d(name, title, xbins=20, xlo=0, xhi=100, ybins=50, ylo=-2.5, yhi=2.5, **kwargs):
    return format_histo2d(name, title, xbins, xlo, xhi, ybins, ylo, yhi, **kwargs)

histos = namespace(
    
    ###########################################
    # Gen Object Histograms
    ###########################################

    genmuon_count = format_histo("CountGenMuons", "CountGenPt20", 10, 0, 10),

    genpt = format_pt_histo("genMuonPt", "Gen Muon Pt"),

    gen_barrel_pt = format_pt_histo("gen_barrel_MuonPt", "Gen Muon Pt"),
    gen_overlap_pt = format_pt_histo("gen_overlap_MuonPt", "Gen Muon Pt"),
    gen_endcap_pt = format_pt_histo("gen_endcap_MuonPt", "Gen Muon Pt"),

    geneta = format_eta_histo("genMuonEta", "Gen Muon Eta"),
    
    gen_barrel_eta = format_eta_histo("gen_barrel_MuonEta", "Gen Muon Eta"),
    gen_overlap_eta = format_eta_histo("gen_overlap_MuonEta", "Gen Muon Eta"),
    gen_endcap_eta = format_eta_histo("gen_endcap_MuonEta", "Gen Muon Eta"),

    gen_2dpteta = format_pteta_histo2d(f"genMuon2DPtEta", "Gen Muon Pt vs Eta"),

    gen_dimuon_m = format_m_histo("genDiMuonMass","Gen Di-Muon Mass;M_{#mu #mu} [GeV];"),

    bestdr = format_histo(f"bestDeltaR_{cfg.branch}_{cfg.label}","Best Delta R", 100, 0, 1),

    ###########################################
    # Matched L1 Gen Object Histograms
    ###########################################

    match_check = format_histo(f"matchCheck_{cfg.branch}_{cfg.label}", "", 10, 0 ,10),

    match_genpt = format_pt_histo(f"matchGen_{cfg.branch}_{cfg.label}_Pt", cfg.label),

    match_gen_barrel_pt = format_pt_histo(f"matchGen_barrel_{cfg.branch}_{cfg.label}_Pt", cfg.label),
    match_gen_overlap_pt = format_pt_histo(f"matchGen_overlap_{cfg.branch}_{cfg.label}_Pt", cfg.label),
    match_gen_endcap_pt = format_pt_histo(f"matchGen_endcap_{cfg.branch}_{cfg.label}_Pt", cfg.label),

    match_geneta = format_eta_histo(f"matchGen_{cfg.branch}_{cfg.label}_Eta", cfg.label),

    match_gen_barrel_eta = format_eta_histo(f"matchGen_barrel_{cfg.branch}_{cfg.label}_Eta", cfg.label),
    match_gen_overlap_eta = format_eta_histo(f"matchGen_overlap_{cfg.branch}_{cfg.label}_Eta", cfg.label),
    match_gen_endcap_eta = format_eta_histo(f"matchGen_endcap_{cfg.branch}_{cfg.label}_Eta", cfg.label),

    match_genphi = format_phi_histo(f"matchGen_{cfg.branch}_{cfg.label}_Phi", cfg.label),
    match_gen_2dpteta = format_pteta_histo2d(f"matchGen_{cfg.branch}_{cfg.label}_2DPtEta", cfg.label),
    
    match_gen_dimuon_m = format_m_histo(f"matchGen_{cfg.branch}_{cfg.label}_DiMuonMass", cfg.label),

    ###########################################
    # Unmatched L1 Gen Object Histograms
    ###########################################

    unmatch_genpt = format_pt_histo(f"noMatchGen_{cfg.branch}_{cfg.label}_Pt", cfg.label),
    unmatch_geneta = format_eta_histo(f"noMatchGen_{cfg.branch}_{cfg.label}_Eta", cfg.label),
    unmatch_genphi = format_phi_histo(f"noMatchGen_{cfg.branch}_{cfg.label}_Phi", cfg.label),

    unmatch_gen_dimuon_m = format_m_histo(f"noMatchGen_{cfg.branch}_{cfg.label}_DiMuonMass", cfg.label),
    ###########################################
    # Matched L1 Object Histograms
    ###########################################

    match_l1pt = format_pt_histo(f"match_l1_{cfg.branch}_{cfg.label}_Pt", cfg.label),
    match_l1eta = format_eta_histo(f"match_l1_{cfg.branch}_{cfg.label}_Eta", cfg.label),
    match_l1phi = format_phi_histo(f"match_l1_{cfg.branch}_{cfg.label}_Phi", cfg.label),

    match_l1ptres = format_histo(f"match_l1_{cfg.branch}_{cfg.label}_ptres","l1 pt - gen pt / gen pt", 100, -1, 1),

    match_l1_dimuon_m = format_m_histo(f"match_l1_{cfg.branch}_{cfg.label}_DiMuonMass", cfg.label),
    ###########################################
    # Efficiency Histograms
    ###########################################

    effi_pt = format_pt_histo(f"effi_{cfg.branch}_{cfg.label}_Pt", cfg.label, color=kRed),

    effi_barrel_pt = format_pt_histo(f"effi_barrel_{cfg.branch}_{cfg.label}_Pt", cfg.label, color=kRed),
    effi_overlap_pt = format_pt_histo(f"effi_overlap_{cfg.branch}_{cfg.label}_Pt", cfg.label, color=kRed),
    effi_endcap_pt = format_pt_histo(f"effi_endcap_{cfg.branch}_{cfg.label}_Pt", cfg.label, color=kRed),

    effi_eta = format_eta_histo(f"effi_{cfg.branch}_{cfg.label}_Eta", cfg.label, color=kRed),
    effi_2dpteta = format_pteta_histo2d(f"effi_{cfg.branch}_{cfg.label}_2DPtEta", cfg.label),
)
print (" ... Loading Gen and L1 Particles")

if cfg.total_events > 0:
    gen_tree = gen_tree[:,cfg.total]
    l1_tree = l1_tree[:,cfg.total]

gen_parts = ak.zip(
    {
        key : gen_tree[field]
        for key, field in cfg.gen_variables.items()
    }, with_name="Momentum4D"
)

l1_parts = ak.zip(
    dict(
    {
        key : l1_tree[field]
        for key, field in cfg.l1_variables.items()
    },
    m = 0.1 * ak.ones_like(l1_tree[f"{cfg.branch}Pt"]),
    ), 
    with_name="Momentum4D"
)
##############################
# Make Gen particle selection 
##############################
print (" ... Masking Gen Particles")

gen_muon_mask = np.abs(gen_tree.partId) == 13
if getattr(cfg, 'gen_selection', None):
    for key, selection in cfg.gen_selection.items():
        print(f' ... ... applying {selection}')
        gen_muon_mask = gen_muon_mask & eval(selection)(gen_tree) 

gen_muon_counts = ak.sum(gen_muon_mask,axis=1)
gen_parts = gen_parts[gen_muon_mask]

gen_barrel_mask = ( np.abs(gen_tree.partEta) < cfg.barrel_eta )[gen_muon_mask]
gen_overlap_mask = (( np.abs(gen_tree.partEta) > cfg.barrel_eta ) & ( np.abs(gen_tree.partEta) < cfg.endcap_eta ))[gen_muon_mask]
gen_endcap_mask = ( np.abs(gen_tree.partEta) > cfg.endcap_eta )[gen_muon_mask]

##############################
# Paring leading gen particles (for now)
# TODO should only pair particles with opposite charges, but charge not what I expected in L1 tree
##############################

print(" ... Pairing Gen Particles")
gen_dimuon = pair_opposite_charged_parts(gen_parts)
fill_th1(histos.gen_dimuon_m, gen_dimuon.m)

##############################
# Fill Gen particle values
##############################

print (" ... Filling Gen Particles")

fill_th1(histos.genmuon_count, gen_muon_counts)

fill_th1(histos.genpt, gen_parts.pt)
fill_th1(histos.gen_barrel_pt, gen_parts.pt[gen_barrel_mask])
fill_th1(histos.gen_overlap_pt, gen_parts.pt[gen_overlap_mask])
fill_th1(histos.gen_endcap_pt, gen_parts.pt[gen_endcap_mask])

fill_th1(histos.geneta, gen_parts.eta)

fill_th1(histos.gen_barrel_eta, gen_parts.eta[gen_barrel_mask])
fill_th1(histos.gen_overlap_eta, gen_parts.eta[gen_overlap_mask])
fill_th1(histos.gen_endcap_eta, gen_parts.eta[gen_endcap_mask])

fill_th2(histos.gen_2dpteta, gen_parts.pt, gen_parts.eta)

##############################
# Make L1 particle selection 
##############################
print (" ... Masking L1 Particles")

l1_muon_mask = l1_parts.pt > 0
if getattr(cfg, 'l1_selection', None):
    for key, selection in cfg.l1_selection.items():
        print(f' ... ... applying {selection}')
        l1_muon_mask = l1_muon_mask & eval(selection)(l1_tree) 

    l1_parts = l1_parts[l1_muon_mask]

##############################
# Find nearest L1 particle in delta R to Gen particle
##############################
print (" ... Matching Gen Particles")

l1_delta_r = get_dr(gen_parts.eta, gen_parts.phi, l1_parts.eta[:,None], l1_parts.phi[:,None])
matched_delta_r, matched_l1_index = ak.min(l1_delta_r, axis=2), ak.argmin(l1_delta_r, axis=2)
fill_th1(histos.bestdr, matched_delta_r)

print (" ... Matched Gen Particles")
matched_mask = matched_delta_r < cfg.matched_delta_r
matched_mask = ak.fill_none(matched_mask, False)

matched_gen = gen_parts[matched_mask]
matched_barrel_mask = gen_barrel_mask[matched_mask]
matched_overlap_mask = gen_overlap_mask[matched_mask]
matched_endcap_mask = gen_endcap_mask[matched_mask]

matched_gen_dimuon = pair_opposite_charged_parts(matched_gen)
##############################
# Fill matched Gen/L1 particle values
##############################
print (" ... Filling Matched Gen Particles")

matched_l1 = l1_parts[matched_l1_index][matched_mask]

ptres = (matched_l1.pt- matched_gen.pt)/matched_gen.pt
matched_l1_dimuon = pair_opposite_hw_charged_parts(matched_l1)

fill_th1(histos.match_check, matched_l1_index)

fill_th1(histos.match_genpt, matched_gen.pt)
fill_th1(histos.match_gen_barrel_pt, matched_gen.pt[matched_barrel_mask])
fill_th1(histos.match_gen_overlap_pt, matched_gen.pt[matched_overlap_mask])
fill_th1(histos.match_gen_endcap_pt, matched_gen.pt[matched_endcap_mask])

fill_th1(histos.match_geneta, matched_gen.eta)
fill_th1(histos.match_gen_barrel_eta, matched_gen.eta[matched_barrel_mask])
fill_th1(histos.match_gen_overlap_eta, matched_gen.eta[matched_overlap_mask])
fill_th1(histos.match_gen_endcap_eta, matched_gen.eta[matched_endcap_mask])

fill_th1(histos.match_genphi, matched_gen.phi)
fill_th2(histos.match_gen_2dpteta, matched_gen.pt, matched_gen.eta)
fill_th1(histos.match_gen_dimuon_m, matched_gen_dimuon.m)

fill_th1(histos.match_l1pt, matched_l1.pt)
fill_th1(histos.match_l1eta, matched_l1.eta)
fill_th1(histos.match_l1phi, matched_l1.phi)
fill_th1(histos.match_l1ptres, ptres)
fill_th1(histos.match_l1_dimuon_m, matched_l1_dimuon.m)

##############################
# Fill unmatched Gen/L1 particle values
##############################
print (" ... Filling Unmatched Gen Particles")
unmatched_gen = gen_parts[~matched_mask]

fill_th1(histos.unmatch_genpt,  unmatched_gen.pt)
fill_th1(histos.unmatch_geneta, unmatched_gen.eta)
fill_th1(histos.unmatch_genphi, unmatched_gen.phi)

# To compute the efficiency: ratio of gen muons matched to l1  over total of
# gen muons (using the binomial option B)
histos.effi_pt.Divide(histos.match_genpt, histos.genpt, 1, 1, "B")

histos.effi_barrel_pt.Divide(histos.match_gen_barrel_pt, histos.gen_barrel_pt, 1, 1, "B")
histos.effi_overlap_pt.Divide(histos.match_gen_overlap_pt, histos.gen_overlap_pt, 1, 1, "B")
histos.effi_endcap_pt.Divide(histos.match_gen_endcap_pt, histos.gen_endcap_pt, 1, 1, "B")

histos.effi_eta.Divide(histos.match_geneta, histos.geneta, 1, 1, "B")
histos.effi_2dpteta.Divide(histos.match_gen_2dpteta, histos.gen_2dpteta, 1, 1, "B")

# SAVE OUTPUT
#################
print(f"Saving  the efficiencies in {cfg.outfile}")

out = TFile(cfg.outfile, "RECREATE")
out.cd()

for key, histo in histos.items():
    histo.Write()
