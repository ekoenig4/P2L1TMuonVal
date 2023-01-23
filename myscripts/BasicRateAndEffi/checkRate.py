# %%
#!/usr/bin/env python3
###############################################################
# Script to compute rates like the menu team did in 2022 
# Directly over the tree: tree.GetEntries( SELECTION STRING )
###############################################################

import uproot as ut
import numpy as np
import awkward as ak
from tqdm import tqdm
import math 

filename = "MB_GMTIso_ID"
myfilepath='/uscms_data/d3/ekoenig/Trigger/Phase2/CMSSW_12_5_2_patch1/src/L1Trigger/P2L1TMuonVal/data/trigger/'

# %%
# f = ut.open(filename + myfilepath + '.root')
tree = ut.lazy(f'{myfilepath}{filename}.root:gmtTkMuonChecksTree/L1PhaseIITree')
entries = len(tree)

# %%
totalrate=31038.0 
# To normalize to total rate at 200:
# 2760.0*11246/1000 = 31038

# Define the additional ID cuts you want to apply:
# (ID="" for no special selection)

# Example: Medium Hw Isolation:
ID="&& gmtTkMuonIso[]>=8"
IDLabel="EXAMPLE_HWISOMR"

eventNo=0

# %%
# Loop over thresholds 
step=(100.-0)/50 # step size
print ('Printing rates!')
print ('====================') 
print ('Bin  Threshold  Rate')

# %%
from ROOT import TH1F, kBlack

class RateProducer:
    def __init__(self, **kwargs):
        self.rates = []
        self.__dict__.update(**kwargs)
    
    def produce(self, i):
        raise NotImplementedError('you should implement this')

    def formatHisto(self, name,title,bins=50,start=0,end=100, color=kBlack):
        histo = TH1F(name,title,bins,start,end)
        histo.SetLineColor(color)
        histo.SetMarkerColor(color)
        histo.SetMarkerStyle(20)
        histo.Sumw2()

        for i, rate in enumerate(self.rates):
            histo.SetBinContent(i, rate)
        self.histo = histo


# %%
class RateGMTTkMuonBarrel(RateProducer):
    def produce(self, i):
        onlinecut = ak.sum((tree["gmtTkMuonPt"] > i*step) \
                        & (tree["gmtTkMuonBx"] == 0) \
                        & (np.abs(tree["gmtTkMuonEta"])<0.83) \
                        & (tree["gmtTkMuonIso"]>=8), axis=-1)>0
        checkRate = ak.sum(onlinecut)*totalrate/entries
        self.rates.append(checkRate)
rateGMTTkMuonBarrel = RateGMTTkMuonBarrel()

# %%
class RateGMTTkMuonEndcap(RateProducer):
    def produce(self, i):
        onlinecut = ak.sum((tree["gmtTkMuonPt"] > i*step) \
                        & (tree["gmtTkMuonBx"] == 0) \
                        & (np.abs(tree["gmtTkMuonEta"])>0.83) \
                        & (np.abs(tree["gmtTkMuonEta"])<1.24) \
                        & (tree["gmtTkMuonIso"]>=8), axis=-1)>0
        checkRate = ak.sum(onlinecut)*totalrate/entries
        self.rates.append(checkRate)
rateGMTTkMuonEndcap = RateGMTTkMuonEndcap()

# %%
class RateGMTTkMuonOverlap(RateProducer):
    def produce(self, i):
        onlinecut = ak.sum((tree["gmtTkMuonPt"] > i*step) \
                        & (tree["gmtTkMuonBx"] == 0) \
                        & (np.abs(tree["gmtTkMuonEta"])>1.24) \
                        & (tree["gmtTkMuonIso"]>=8), axis=-1)>0
        checkRate = ak.sum(onlinecut)*totalrate/entries
        self.rates.append(checkRate)
rateGMTTkMuonOverlap = RateGMTTkMuonOverlap()

# %%
class RateGMTTkMuonAll(RateProducer):
    def produce(self, i):
        onlinecut = ak.sum((tree["gmtTkMuonPt"] > i*step) \
                        & (tree["gmtTkMuonBx"] == 0) \
                        & (tree["gmtTkMuonIso"]>=8), axis=-1)>0
        checkRate = ak.sum(onlinecut)*totalrate/entries
        self.rates.append(checkRate)
rateGMTTkMuonAll = RateGMTTkMuonAll()

# %%
for i in tqdm(range(0, 40)): 
    rateGMTTkMuonBarrel.produce(i)
    rateGMTTkMuonEndcap.produce(i)
    rateGMTTkMuonOverlap.produce(i)
    rateGMTTkMuonAll.produce(i)

# %%
from ROOT import TFile

out = TFile(f"my_rate_{filename}_{IDLabel}.root","recreate")
out.cd()

# %%
rateGMTTkMuonBarrel.formatHisto("rateGMTTkMuonBarrel","Rate GMTTkMuon Barrel")
rateGMTTkMuonEndcap.formatHisto("rateGMTTkMuonEndcap","Rate GMTTkMuon Endcap")
rateGMTTkMuonOverlap.formatHisto("rateGMTTkMuonOverlap","Rate GMTTkMuon Overlap")
rateGMTTkMuonAll.formatHisto("rateGMTTkMuonAll","Rate GMTTkMuon All")

# %%
rateGMTTkMuonBarrel.histo.Write()
rateGMTTkMuonEndcap.histo.Write()
rateGMTTkMuonOverlap.histo.Write()
rateGMTTkMuonAll.histo.Write()

# %%
out.Close()

# %%



