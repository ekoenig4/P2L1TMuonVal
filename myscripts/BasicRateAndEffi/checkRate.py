###############################################################
# Script to compute rates like the menu team did in 2022
# Directly over the tree: tree.GetEntries( SELECTION STRING )
###############################################################


#!/usr/bin/env python
from ROOT import *
import math, sys, git, os
TH1.GetDefaultSumw2()

sys.path.append( git.Repo('.', search_parent_directories=True).working_tree_dir )
from myscripts.phase2_utils.yaml_cfg import Config


cfg = Config(f'{os.path.dirname(__file__)}/config/gmt_tk_muon_rates.yaml')
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

# Format for the rate histograms:
def formatHisto(name, title, bins=cfg.formatHisto['bins'], start=cfg.formatHisto['start'], end=cfg.formatHisto['end'], color=cfg.formatHisto['color']):
    histo = TH1F(name, title, bins, start, end)
    histo.SetLineColor(globals()[color])
    histo.SetMarkerColor(globals()[color])
    histo.SetMarkerStyle(20)
    histo.Sumw2()
    return histo


for rate, info in cfg.rates.items():
    info['histo'] = formatHisto(rate, info['title'])

# Loop over thresholds
step = (cfg.formatHisto['end']-cfg.formatHisto['start'])/cfg.formatHisto['bins']  # step size
print('Printing rates!')
print('====================')
print('Bin  Threshold  Rate')

for i in range(0, 40):

    for rate, info in cfg.rates.items():
        onlinecut = f"Sum$( {' && '.join(info['onlinecut'])} )>0"
        onlinecut = onlinecut.format(step=i*step, ID=cfg.ID)
        checkRate = tree.GetEntries(onlinecut)*cfg.totalrate/entries
        info['histo'].SetBinContent(i, checkRate)

    # print total rate for debugging
    print("%d  %.1f %d" % (i, i*step, checkRate))

# Save the rate histograms:

out = TFile(cfg.outfile.format(file=cfg.file, IDLabel=cfg.IDLabel), "RECREATE")
out.cd()

for rate, info in cfg.rates.items():
    info['histo'].Write()