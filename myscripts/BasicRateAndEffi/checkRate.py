###############################################################
# Script to compute rates like the menu team did in 2022
# Directly over the tree: tree.GetEntries( SELECTION STRING )
###############################################################


#!/usr/bin/env python
from ROOT import *
import math, sys, git, os
TH1.GetDefaultSumw2()

from L1Trigger.Phase2L1GMTNtuples.yaml_cfg import Config

cfg = Config.from_file(f'{os.path.dirname(__file__)}/config/rate_gmt_tk_muon.yaml')
cfg.parse_args()

# filename="MinBias_GMTIso"
# myfilepath='/nfs/cms/cepeda/trigger/'
# filename = "MB_GMTIso_ID"
# myfilepath = '/eos/user/c/cepeda/trigger/'

f = TFile(f'{cfg.filepath}/{cfg.file}.root')
# tree = f.Get("l1PhaseIITree/L1PhaseIITree") # this is the menu tree
tree = f.Get("gmtTkMuonChecksTree/L1PhaseIITree")  # this is the menu tree
entries = tree.GetEntriesFast()

# To normalize to total rate at 200:
# 2760.0*11246/1000 = 31038

# Define the additional ID cuts you want to apply:
# (ID="" for no special selection)

# Example: Medium Hw Isolation:

eventNo = 0


class RateHisto:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        self.formatHisto()
        
# Format for the rate histograms:
    def formatHisto(self):
        histo = TH1F(self.name, self.title, self.bins, self.start, self.end)
        histo.SetLineColor(globals()[self.color])
        histo.SetMarkerColor(globals()[self.color])
        histo.SetMarkerStyle(20)
        histo.Sumw2()
        self.histo = histo


for name, info in cfg.rates.items():
    cfg.rates[name] = RateHisto(name=name, **info, **cfg.formatHisto)

# Loop over thresholds
step = (cfg.formatHisto['end']-cfg.formatHisto['start'])/cfg.formatHisto['bins']  # step size
print('Printing rates!')
print('====================')
print('Bin  Threshold  Rate')

for i in range(0, 40):

    for name, rate in cfg.rates.items():
        onlinecut = f"Sum$( {' && '.join(rate.onlinecut)} )>0"
        onlinecut = onlinecut.format(step=i*step, ID=cfg.ID)
        checkRate = tree.GetEntries(onlinecut)*cfg.totalrate/entries
        rate.histo.SetBinContent(i, checkRate)

    # print total rate for debugging
    print(f"{i} {i*step:0.1f} {checkRate:0.1f}")

# Save the rate histograms:

out = TFile(cfg.outfile.format(file=cfg.file, IDLabel=cfg.IDLabel), "RECREATE")
out.cd()

for name, rate in cfg.rates.items():
    rate.histo.Write()