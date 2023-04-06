#!/bin/sh

SCRIPT=myscripts/BasicRateAndEffi/diMuonSimple.py

python3 $SCRIPT --help

dy10=input/DYToLL_M-10To50_TuneCP5_14TeV-pythia8.txt
dy50=input/DYToLL_M-50_TuneCP5_14TeV-pythia8.txt

########################
# Produce GMT Tracker Muon 
# python3 $SCRIPT --file $dy10 --branch gmtTkMuon --label DYToLL_M-10To50 $@ 
# python3 $SCRIPT --file $dy50 --branch gmtTkMuon --label DYToLL_M-50 $@

########################
# Produce GMT Standalone Muon 

# python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50 $@
# python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50 $@

# python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50_unscaled --unscale-l1-muon-pt True $@ 
# python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50_unscaled --unscale-l1-muon-pt True $@

python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50_lut6_unscaled --unscale-l1-muon-pt True --lutversion 6$@ 
python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50_lut6_unscaled --unscale-l1-muon-pt True --lutversion 6 $@