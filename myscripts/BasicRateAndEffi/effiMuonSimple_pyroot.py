###############################################################
# Script to compute rates like the menu team did in 2022
# Directly over the tree: tree.GetEntries( SELECTION STRING )
###############################################################


#!/usr/bin/env python
from ROOT import *
import math, sys, git, os, tqdm, numpy as np
TH1.GetDefaultSumw2()

from L1Trigger.Phase2L1GMTNtuples.yaml_cfg import Config
from L1Trigger.Phase2L1GMTNtuples.variable_collection import variable_collection
from L1Trigger.Phase2L1GMTNtuples.format_histo import format_histo, format_histo2d

cfg = Config.from_file(f'{os.path.dirname(__file__)}/config/effi_gmt_tk_muon.yaml')
cfg.parse_args()

filename = f'{cfg.filepath}/{cfg.file}.root'
f = TFile(filename)
# tree = f.Get("l1PhaseIITree/L1PhaseIITree") # this is the menu tree
tree = f.Get("gmtTkMuonChecksTree/L1PhaseIITree")  # this is the menu tree
tree.AddFriend("genTree/L1GenTree", f)
entries = tree.GetEntriesFast()

TH1.GetDefaultSumw2()

def delta_r(eta_1, phi_1, eta_2, phi_2):
    delta_eta = abs(eta_2 - eta_1)
    delta_phi = TVector2.Phi_mpi_pi(phi_2 - phi_1)
    return math.sqrt(delta_eta**2 + delta_phi**2)

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
    entries = cfg.total

it = enumerate(tree)
it = tqdm.tqdm(it, total=entries)
for i, event in it:
    if i == entries: break

    gen_count = 0
    
    vectorPt = getattr(event, cfg.branch+"Pt")  # GMT Muons
    vectorEta = getattr(event, cfg.branch+"Eta")
    vectorPhi = getattr(event, cfg.branch+"Phi")
    vectorStubs = getattr(event, cfg.branch+"NStubs")

    vectorGenPt = getattr(event, "partPt")  # Gen Particles
    vectorGenEta = getattr(event, "partEta")
    vectorGenPhi = getattr(event, "partPhi")
    vectorGenId = getattr(event, "partId")
    vectorGenStat = getattr(event, "partStat")

    for i in range(vectorGenPt.size()):
        if not ( vectorGenStat[i] == 1 ): continue
        if not ( abs(vectorGenId[i]) == 13 ): continue 
        if not ( abs(vectorGenEta[i]) > cfg.eta_range[0] ): continue
        if not ( abs(vectorGenEta[i]) < cfg.eta_range[1] ): continue
        if not ( abs(vectorGenPt[i])  > cfg.pt_range[0] ): continue
        if not ( abs(vectorGenPt[i])  < cfg.pt_range[1] ): continue

        histos.genpt.Fill(vectorGenPt[i])
        histos.geneta.Fill(vectorGenEta[i])
        histos.gen_2dpteta.Fill(vectorGenPt[i], vectorGenEta[i])
        gen_count += 1

        l1_delta_r = [ 
            delta_r(vectorGenEta[i], vectorGenPhi[i], vectorEta[j], vectorPhi[j]) 
            for j in range(vectorPt.size())
        ]

        matched_delta_r = min( l1_delta_r + [np.inf] )
        histos.bestdr.Fill(matched_delta_r)

        if matched_delta_r < cfg.matched_delta_r:
            matched_l1_index = l1_delta_r.index(matched_delta_r)

            ptres = (vectorPt[matched_l1_index] - vectorGenPt[i])/vectorGenPt[i]

            histos.match_genpt.Fill(vectorGenPt[i])
            histos.match_geneta.Fill(vectorGenEta[i])
            histos.match_genphi.Fill(vectorGenPhi[i])
            histos.match_gen_2dpteta.Fill(vectorGenPt[i], vectorGenEta[i])
            histos.match_check.Fill(matched_l1_index)

            histos.match_l1pt.Fill(vectorPt[matched_l1_index])
            histos.match_l1eta.Fill(vectorEta[matched_l1_index])
            histos.match_l1phi.Fill(vectorPhi[matched_l1_index])
            histos.match_l1ptres.Fill(ptres)
        else:
            histos.unmatch_genpt.Fill(vectorGenPt[i])
            histos.unmatch_geneta.Fill(vectorGenEta[i])
            histos.unmatch_genphi.Fill(vectorGenPhi[i])

    histos.gencount.Fill(gen_count)

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
