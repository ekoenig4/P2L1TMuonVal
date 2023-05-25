#!/usr/bin/env python3
###############################################################
# python3 myscripts/BasicRateAndEffi/dimuonSimple.py --help
###############################################################


import os

import awkward as ak
import numpy as np
import uproot as ut
import vector
from L1Trigger.Phase2L1GMTNtuples.hep_tools import get_dr,pair_leading_parts
from L1Trigger.Phase2L1GMTNtuples.root_tools import (fill_th1, fill_th2,
                                                     format_histo,
                                                     format_histo2d)
from L1Trigger.Phase2L1GMTNtuples.scaling_tools import unscale_l1_muon_pt, menu_scaling_l1_muon_pt
from L1Trigger.Phase2L1GMTNtuples.yaml_cfg import Config
from L1Trigger.Phase2L1GMTNtuples.glob_tools import get_filelist
from ROOT import *

vector.register_awkward()
TH1.GetDefaultSumw2()


cfg = Config.from_file(f'{os.path.dirname(__file__)}/config/di_gmt_muon.yaml').init()

cfg.pt_range = (cfg.pt_min, cfg.pt_max)
cfg.eta_range = (cfg.eta_min, cfg.eta_max)

filelist = get_filelist(cfg.files)

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


gen_config = namespace(**cfg.gen_tree)
gen_tree = ut.lazy( [f"{f}:{gen_config.tree}" for f in filelist] )

l1_config = namespace(**cfg.l1_tree)
l1_tree = ut.lazy( [f"{f}:{l1_config.tree}" for f in filelist] )

gen_entries = len(gen_tree)
l1_entries = len(l1_tree)

if l1_entries != gen_entries:
    raise ValueError()

entries = gen_entries

TH1.GetDefaultSumw2()

print("=========================================================")
print("Computing L1/Gen DiMuon Distributions from %i file(s)" % (len(filelist)))
print("\n".join(f" ... {f}" for f in filelist))
print("Total Events: %d" % entries)
print("Pt Range: %.0f - %.0f" % tuple(cfg.pt_range))
print("Eta Range: %.1f - %.1f" % tuple(cfg.eta_range))
print("=========================================================")


def format_pt_histo(name, title, bins=20, lo=0, hi=100, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_eta_histo(name, title, bins=50, lo=-2.5, hi=2.5, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_phi_histo(name, title, bins=100, lo=-4, hi=4, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_m_histo(name, title, bins=100, lo=0, hi=200, **kwargs):
    return format_histo(name, title, bins, lo, hi, **kwargs)
def format_pteta_histo2d(name, title, xbins=20, xlo=0, xhi=100, ybins=50, ylo=-2.5, yhi=2.5, **kwargs):
    return format_histo2d(name, title, xbins, xlo, xhi, ybins, ylo, yhi, **kwargs)

histos = namespace(
    
    ###########################################
    # Gen Object Histograms
    ###########################################
    genmuon_count = format_histo("CountGenMuons", "CountGenPt20", 10, 0, 10),

    genpt = format_pt_histo("genMuonPt", "Gen Muon Pt"),
    geneta = format_eta_histo("genMuonEta", "Gen Muon Eta"),
    gen_2dpteta = format_pteta_histo2d(f"genMuon2DPtEta", "Gen Muon Pt vs Eta"),

    gen_dimuon_m = format_m_histo("genDiMuonMass","Gen Di-Muon Mass;M_{#mu #mu} [GeV];"),

    gen_bb_dimuon_m = format_m_histo("gen_bb_DiMuonMass", "Gen Di-Muon Mass barrel-barrel;M_{#mu #mu} [GeV];"),
    gen_bo_dimuon_m = format_m_histo("gen_bo_DiMuonMass", "Gen Di-Muon Mass barrel-overlap;M_{#mu #mu} [GeV];"),
    gen_be_dimuon_m = format_m_histo("gen_be_DiMuonMass", "Gen Di-Muon Mass barrel-endcap;M_{#mu #mu} [GeV];"),
    # gen_bc_dimuon_m = format_m_histo("gen_bc_DiMuonMass", "Gen Di-Muon Mass barrel-center endcap;M_{#mu #mu} [GeV];"),
    # gen_bf_dimuon_m = format_m_histo("gen_bf_DiMuonMass", "Gen Di-Muon Mass barrel-forward endcap;M_{#mu #mu} [GeV];"),
    
    gen_oo_dimuon_m = format_m_histo("gen_oo_DiMuonMass", "Gen Di-Muon Mass overlap-overlap;M_{#mu #mu} [GeV];"),
    gen_oe_dimuon_m = format_m_histo("gen_oe_DiMuonMass", "Gen Di-Muon Mass overlap-endcap;M_{#mu #mu} [GeV];"),
    # gen_oc_dimuon_m = format_m_histo("gen_oc_DiMuonMass", "Gen Di-Muon Mass overlap-center endcap;M_{#mu #mu} [GeV];"),
    # gen_of_dimuon_m = format_m_histo("gen_of_DiMuonMass", "Gen Di-Muon Mass overlap-forward endcap;M_{#mu #mu} [GeV];"),
    
    gen_ee_dimuon_m = format_m_histo("gen_ee_DiMuonMass", "Gen Di-Muon Mass endcap-endcap;M_{#mu #mu} [GeV];"),
    # gen_cc_dimuon_m = format_m_histo("gen_cc_DiMuonMass", "Gen Di-Muon Mass center endcap-center endcap;M_{#mu #mu} [GeV];"),
    # gen_cf_dimuon_m = format_m_histo("gen_cf_DiMuonMass", "Gen Di-Muon Mass center endcap-forward endcap;M_{#mu #mu} [GeV];"),
    # gen_ff_dimuon_m = format_m_histo("gen_ff_DiMuonMass", "Gen Di-Muon Mass forward endcap-forward endcap;M_{#mu #mu} [GeV];"),

    ###########################################
    # L1 Object Histograms
    ###########################################
    l1pt = format_pt_histo(f"l1_{cfg.branch}_Pt", cfg.label),
    l1eta = format_eta_histo(f"l1_{cfg.branch}_Eta", cfg.label),
    l1phi = format_phi_histo(f"l1_{cfg.branch}_Phi", cfg.label),

    l1_dimuon_m = format_m_histo(f"l1_{cfg.branch}_DiMuonMass", cfg.label),

    l1_bb_dimuon_m = format_m_histo(f"l1_bb_{cfg.branch}_DiMuonMass", cfg.label),
    l1_bo_dimuon_m = format_m_histo(f"l1_bo_{cfg.branch}_DiMuonMass", cfg.label),
    l1_be_dimuon_m = format_m_histo(f"l1_be_{cfg.branch}_DiMuonMass", cfg.label),
    # l1_bc_dimuon_m = format_m_histo(f"l1_bc_{cfg.branch}_DiMuonMass", cfg.label),
    # l1_bf_dimuon_m = format_m_histo(f"l1_bf_{cfg.branch}_DiMuonMass", cfg.label),

    l1_oo_dimuon_m = format_m_histo(f"l1_oo_{cfg.branch}_DiMuonMass", cfg.label),
    l1_oe_dimuon_m = format_m_histo(f"l1_oe_{cfg.branch}_DiMuonMass", cfg.label),
    # l1_oc_dimuon_m = format_m_histo(f"l1_oc_{cfg.branch}_DiMuonMass", cfg.label),
    # l1_of_dimuon_m = format_m_histo(f"l1_of_{cfg.branch}_DiMuonMass", cfg.label),

    l1_ee_dimuon_m = format_m_histo(f"l1_ee_{cfg.branch}_DiMuonMass", cfg.label),
    # l1_cc_dimuon_m = format_m_histo(f"l1_cc_{cfg.branch}_DiMuonMass", cfg.label),
    # l1_cf_dimuon_m = format_m_histo(f"l1_cf_{cfg.branch}_DiMuonMass", cfg.label),
    # l1_ff_dimuon_m = format_m_histo(f"l1_ff_{cfg.branch}_DiMuonMass", cfg.label),
    
)
print (" ... Loading Gen and L1 Particles")

if cfg.total > 0:
    gen_tree = gen_tree[:cfg.total]
    l1_tree = l1_tree[:cfg.total]

gen_parts = ak.zip(
    dict({
        key : gen_tree[field]
        for key, field in gen_config.variables.items()
    },
    m = cfg.muon_mass * ak.ones_like(gen_tree[f"partPt"]),
    ), 
    with_name="Momentum4D"
)

l1_parts = ak.zip(
    dict({
        key : l1_tree[field]
        for key, field in l1_config.variables.items()
    },
    m = cfg.muon_mass * ak.ones_like(l1_tree[f"{cfg.branch}Pt"]),
    ), 
    with_name="Momentum4D"
)
##############################
# Make Gen particle selection 
##############################
print (" ... Masking Gen Particles")

gen_muon_mask = np.abs(gen_tree.partId) == 13
if getattr(gen_config, 'selection', None):
    for key, selection in gen_config.selection.items():
        print(f' ... ... applying {selection}')
        gen_muon_mask = gen_muon_mask & eval(selection)(gen_tree) 

gen_muon_counts = ak.sum(gen_muon_mask,axis=1)
gen_parts = gen_parts[gen_muon_mask]

##############################
# Paring leading gen particles (for now)
# TODO should only pair particles with opposite charges, but charge not what I expected in L1 tree
##############################

print(" ... Pairing Gen Particles")
gen_dimuon, gen_dimuon_mask = pair_leading_parts(gen_parts, return_mask=True)
gen_muons = gen_parts[gen_dimuon_mask][:,:2]

fill_th1(histos.gen_dimuon_m, gen_dimuon.m)

n_gen_barrel_muons = ak.sum( np.abs(gen_muons.eta) < cfg.barrel_eta, axis=1)
n_gen_overlap_muons = ak.sum( (np.abs(gen_muons.eta) > cfg.barrel_eta) & (np.abs(gen_muons.eta) < cfg.endcap_eta), axis=1)
n_gen_endcap_muons = ak.sum( np.abs(gen_muons.eta) > cfg.endcap_eta, axis=1)
n_gen_center_endcap_muons = ak.sum( (np.abs(gen_muons.eta) > cfg.endcap_eta) & (np.abs(gen_muons.eta) < cfg.eta_max), axis=1)
n_gen_forward_endcap_muons = ak.sum( (np.abs(gen_muons.eta) > cfg.endcap_eta) & (np.abs(gen_muons.eta) > cfg.eta_max), axis=1)

fill_th1(histos.gen_bb_dimuon_m, gen_dimuon.m[(n_gen_barrel_muons == 2)])
fill_th1(histos.gen_bo_dimuon_m, gen_dimuon.m[(n_gen_barrel_muons == 1) & (n_gen_overlap_muons == 1)])
fill_th1(histos.gen_be_dimuon_m, gen_dimuon.m[(n_gen_barrel_muons == 1) & (n_gen_endcap_muons == 1)])
# fill_th1(histos.gen_bc_dimuon_m, gen_dimuon.m[(n_gen_barrel_muons == 1) & (n_gen_center_endcap_muons == 1)])
# fill_th1(histos.gen_bf_dimuon_m, gen_dimuon.m[(n_gen_barrel_muons == 1) & (n_gen_forward_endcap_muons == 1)])

fill_th1(histos.gen_oo_dimuon_m, gen_dimuon.m[(n_gen_overlap_muons == 2)])
fill_th1(histos.gen_oe_dimuon_m, gen_dimuon.m[(n_gen_overlap_muons == 1) & (n_gen_endcap_muons == 1)])
# fill_th1(histos.gen_oc_dimuon_m, gen_dimuon.m[(n_gen_overlap_muons == 1) & (n_gen_center_endcap_muons == 1)])
# fill_th1(histos.gen_of_dimuon_m, gen_dimuon.m[(n_gen_overlap_muons == 1) & (n_gen_forward_endcap_muons == 1)])

fill_th1(histos.gen_ee_dimuon_m, gen_dimuon.m[(n_gen_endcap_muons == 2)])
# fill_th1(histos.gen_cc_dimuon_m, gen_dimuon.m[(n_gen_center_endcap_muons == 2)])
# fill_th1(histos.gen_cf_dimuon_m, gen_dimuon.m[(n_gen_center_endcap_muons == 1) & (n_gen_forward_endcap_muons == 1)])
# fill_th1(histos.gen_ff_dimuon_m, gen_dimuon.m[(n_gen_forward_endcap_muons == 2)])

##############################
# Fill Gen particle values
##############################

print (" ... Filling Gen Particles")

fill_th1(histos.genmuon_count, gen_muon_counts)

fill_th1(histos.genpt, gen_parts.pt)
fill_th1(histos.geneta, gen_parts.eta)
fill_th2(histos.gen_2dpteta, gen_parts.pt, gen_parts.eta)

##############################
# Make L1 particle selection 
##############################
print (" ... Masking L1 Particles")

l1_muon_mask = l1_parts.pt > 0
if getattr(l1_config, 'selection', None):
    for key, selection in l1_config.selection.items():
        print(f' ... ... applying {selection}')
        l1_muon_mask = l1_muon_mask & eval(selection)(l1_tree) 

    l1_parts = l1_parts[l1_muon_mask]


##############################
# Find nearest L1 particle in delta R to Gen particle
##############################
print (" ... Matching Gen Particles")

l1_delta_r = get_dr(gen_parts.eta, gen_parts.phi, l1_parts.eta[:,None], l1_parts.phi[:,None])
matched_delta_r, matched_l1_index = ak.min(l1_delta_r, axis=2), ak.argmin(l1_delta_r, axis=2)
# fill_th1(histos.bestdr, matched_delta_r)

print (" ... Matched Gen Particles")
matched_mask = matched_delta_r < cfg.matched_delta_r
matched_mask = ak.fill_none(matched_mask, False)

##############################
# Fill matched Gen/L1 particle values
##############################
print (" ... Filling L1 Particles")

l1 = l1_parts[matched_l1_index][matched_mask]

l1_muon_pt = l1.pt
if cfg.unscale_l1_muon_pt:
    print("Applying unscaling")
    l1_muon_pt = unscale_l1_muon_pt(l1_muon_pt, l1.eta, barrel_eta=cfg.barrel_eta, endcap_eta=cfg.endcap_eta, lutversion=cfg.lutversion)

if cfg.menu_l1_muon_pt:
    print("Applying menu scaling")
    l1_muon_pt = menu_scaling_l1_muon_pt(l1_muon_pt, l1.eta, barrel_eta=cfg.barrel_eta, endcap_eta=cfg.endcap_eta)

if cfg.unscale_l1_muon_pt or cfg.menu_l1_muon_pt:
    l1 = ak.zip(
        dict(
            pt=l1_muon_pt,
            eta=l1.eta,
            phi=l1.phi,
            m=l1.m
        ),
        with_name="Momentum4D",
        depth_limit=1,
    )

l1_dimuon, l1_dimuon_mask = pair_leading_parts(l1, return_mask=True)
l1_muons = l1[l1_dimuon_mask][:,:2]

n_l1_barrel_muons = ak.sum( np.abs(l1_muons.eta) < cfg.barrel_eta, axis=1)
n_l1_overlap_muons = ak.sum( (np.abs(l1_muons.eta) > cfg.barrel_eta) & (np.abs(l1_muons.eta) < cfg.endcap_eta), axis=1)
n_l1_endcap_muons = ak.sum( np.abs(l1_muons.eta) > cfg.endcap_eta, axis=1)
n_l1_center_endcap_muons = ak.sum( (np.abs(l1_muons.eta) > cfg.endcap_eta) & (np.abs(l1_muons.eta) < cfg.eta_max), axis=1)
n_l1_forward_endcap_muons = ak.sum( (np.abs(l1_muons.eta) > cfg.endcap_eta) & (np.abs(l1_muons.eta) > cfg.eta_max), axis=1)

fill_th1(histos.l1_bb_dimuon_m, l1_dimuon.m[(n_l1_barrel_muons == 2)])
fill_th1(histos.l1_bo_dimuon_m, l1_dimuon.m[(n_l1_barrel_muons == 1) & (n_l1_overlap_muons == 1)])
fill_th1(histos.l1_be_dimuon_m, l1_dimuon.m[(n_l1_barrel_muons == 1) & (n_l1_endcap_muons == 1)])
# fill_th1(histos.l1_bc_dimuon_m, l1_dimuon.m[(n_l1_barrel_muons == 1) & (n_l1_center_endcap_muons == 1)])
# fill_th1(histos.l1_bf_dimuon_m, l1_dimuon.m[(n_l1_barrel_muons == 1) & (n_l1_forward_endcap_muons == 1)])

fill_th1(histos.l1_oo_dimuon_m, l1_dimuon.m[(n_l1_overlap_muons == 2)])
fill_th1(histos.l1_oe_dimuon_m, l1_dimuon.m[(n_l1_overlap_muons == 1) & (n_l1_endcap_muons == 1)])
# fill_th1(histos.l1_oc_dimuon_m, l1_dimuon.m[(n_l1_overlap_muons == 1) & (n_l1_center_endcap_muons == 1)])
# fill_th1(histos.l1_of_dimuon_m, l1_dimuon.m[(n_l1_overlap_muons == 1) & (n_l1_forward_endcap_muons == 1)])

fill_th1(histos.l1_ee_dimuon_m, l1_dimuon.m[(n_l1_endcap_muons == 2)])
# fill_th1(histos.l1_cc_dimuon_m, l1_dimuon.m[(n_l1_center_endcap_muons == 2)])
# fill_th1(histos.l1_cf_dimuon_m, l1_dimuon.m[(n_l1_center_endcap_muons == 1) & (n_l1_forward_endcap_muons == 1)])
# fill_th1(histos.l1_ff_dimuon_m, l1_dimuon.m[(n_l1_forward_endcap_muons == 2)])

fill_th1(histos.l1pt, l1.pt)
fill_th1(histos.l1eta, l1.eta)
fill_th1(histos.l1phi, l1.phi)
fill_th1(histos.l1_dimuon_m, l1_dimuon.m)

# SAVE OUTPUT
#################
print(f"Saving  the dimuon distributions in {cfg.outfile}")

out = TFile(cfg.outfile, "RECREATE")
out.cd()

for key, histo in histos.items():
    histo.Write()
