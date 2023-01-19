# P2L1TMuonVal

This repository will contain an example tree and python analysis code to perform P2 L1TMuon checks for gmtMuons (with and without tracks) 

Existing ntuples: /eos/user/c/cepeda/trigger/ (DoubleMuGun for signal and MinBias for backgound)

# Installing

Code runs in [CMSSW_12_5_2_patch1]
```
cmsrel CMSSW_12_5_2_patch1
cd CMSSW_12_5_2_patch1/src
cmsenv
git cms-init
git cms-merge-topic -u cms-l1t-offline:l1t-phase2-v51-CMSSW_12_5_2_patch1
scram b -j 8
```

After CMSSW installs
```
cd ${CMSSW_BASE}/src/L1Trigger/
git clone https://github.com/ekoenig4/P2L1TMuonVal.git
cd P2L1TMuonVal
scram b
```
