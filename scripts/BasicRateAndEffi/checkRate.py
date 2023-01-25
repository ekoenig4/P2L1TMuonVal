###############################################################
# Script to compute rates like the menu team did in 2022
# Directly over the tree: tree.GetEntries( SELECTION STRING )
###############################################################


#!/usr/bin/env python
# from ROOT import *
from ROOT import TH1, TFile, kBlack, TH1F
import math
TH1.GetDefaultSumw2()

# filename="MinBias_GMTIso"
# myfilepath='/nfs/cms/cepeda/trigger/'
filename = "MB_GMTIso_ID"
# myfilepath = '/eos/user/c/cepeda/trigger/'
myfilepath = 'data/trigger/'

f = TFile(myfilepath+filename+'.root')
# tree = f.Get("l1PhaseIITree/L1PhaseIITree") # this is the menu tree
tree = f.Get("gmtTkMuonChecksTree/L1PhaseIITree")  # this is the menu tree
branch = "gmtTkMuon"
entries = tree.GetEntriesFast()

totalrate = 31038.0
# To normalize to total rate at 200:
# 2760.0*11246/1000 = 31038

# Define the additional ID cuts you want to apply:
# (ID="" for no special selection)

# Example: Medium Hw Isolation:
ID = "&& gmtTkMuonIso[]>=8"
IDLabel = "EXAMPLE_HWISOMR"

eventNo = 0

# Format for the rate histograms:


def formatHisto(name, title, bins=50, start=0, end=100, color=kBlack):
    histo = TH1F(name, title, bins, start, end)
    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetMarkerStyle(20)
    histo.Sumw2()
    return histo


rateGMTTkMuonBarrel = formatHisto(
    "rateGMTTkMuonBarrel", "Rate GMTTkMuon Barrel;GMT Track Muon Pt;Rate")
rateGMTTkMuonEndcap = formatHisto(
    "rateGMTTkMuonEndcap", "Rate GMTTkMuon Endcap;GMT Track Muon Pt;Rate")
rateGMTTkMuonOverlap = formatHisto(
    "rateGMTTkMuonOverlap", "Rate GMTTkMuon Overlap;GMT Track Muon Pt;Rate")
rateGMTTkMuonAll = formatHisto(
    "rateGMTTkMuonAll", "Rate GMTTkMuon All;GMT Track Muon Pt;Rate")

# Loop over thresholds
step = (100.-0)/50  # step size
print('Printing rates!')
print('====================')
print('Bin  Threshold  Rate')

for i in range(0, 40):

    # Full Selection String: count the muons passing the cuts. Barrel only!
    onlinecut = "Sum$( gmtTkMuonPt[]>"+str(i*step) + \
        "&& gmtTkMuonBx[]==0 && abs(gmtTkMuonEta[])<0.83"+ID+")>0 "
    # Here you compute the rate for one threshold and normalize it!:
    checkRate = tree.GetEntries(onlinecut)*totalrate/entries
    # Fill the histogram
    rateGMTTkMuonBarrel.SetBinContent(i, checkRate)

    # Repeat for overlap
    onlinecut = "Sum$( gmtTkMuonPt[]>"+str(i*step) + \
        "&& gmtTkMuonBx[]==0 &&abs(gmtTkMuonEta[])>0.83 && abs(gmtTkMuonEta[])<1.24" + ID+")>0 "
    checkRate = tree.GetEntries(onlinecut)*totalrate/entries
    rateGMTTkMuonOverlap.SetBinContent(i, checkRate)

    # Repeat for endcap
    onlinecut = "Sum$( gmtTkMuonPt[]>"+str(i*step) + \
        "&& gmtTkMuonBx[]==0 &&abs(gmtTkMuonEta[])>1.24"+ID+")>0 "
    checkRate = tree.GetEntries(onlinecut)*totalrate/entries
    rateGMTTkMuonEndcap.SetBinContent(i, checkRate)

    # All eta
    onlinecut = "Sum$( gmtTkMuonPt[]>"+str(i*step) + \
        "&& gmtTkMuonBx[]==0"+ID+")>0 "
    checkRate = tree.GetEntries(onlinecut)*totalrate/entries
    # print total rate for debugging
    print("%d  %.1f %d" % (i, i*step, checkRate))
    rateGMTTkMuonAll.SetBinContent(i, checkRate)

# Save the rate histograms:

out = TFile("rate_"+filename+"_"+IDLabel+".root", "RECREATE")
out.cd()

rateGMTTkMuonBarrel.Write()
rateGMTTkMuonOverlap.Write()
rateGMTTkMuonEndcap.Write()
rateGMTTkMuonAll.Write()
