#!/bin/sh

SCRIPT=myscripts/BasicRateAndEffi/diMuonSimple.py

python3 $SCRIPT --help

dy10=input/DYToLL_M-10To50_TuneCP5_14TeV-pythia8.txt
dy50=input/DYToLL_M-50_TuneCP5_14TeV-pythia8.txt

export ARGS=$@
torun() {

########################
# Produce GMT Tracker Muon 
# echo python3 $SCRIPT --file $dy10 --branch gmtTkMuon --label DYToLL_M-10To50 $ARGS 
# echo python3 $SCRIPT --file $dy50 --branch gmtTkMuon --label DYToLL_M-50 $ARGS

########################
# Produce GMT Standalone Muon 

# echo python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50 $ARGS
# echo python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50 $ARGS

# echo python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50_eta1p2-1p6 --eta-min 1.2 --eta-max 1.6 $ARGS 
# echo python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50_eta1p2-1p6 --eta-min 1.2 --eta-max 1.6 $ARGS

# echo python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50_unscaled --unscale-l1-muon-pt True $ARGS 
# echo python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50_unscaled --unscale-l1-muon-pt True $ARGS

echo python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50_menu --menu-l1-muon-pt True $ARGS 
echo python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50_menu --menu-l1-muon-pt True $ARGS

# echo python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50_unscaled_eta1p2-1p6 --eta-min 1.2 --eta-max 1.6 --unscale-l1-muon-pt True $ARGS 
# echo python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50_unscaled_eta1p2-1p6 --eta-min 1.2 --eta-max 1.6 --unscale-l1-muon-pt True $ARGS

# echo python3 $SCRIPT --file $dy10 --branch gmtSaMuon --label DYToLL_M-10To50_lut6_unscaled --unscale-l1-muon-pt True --lutversion 6$ARGS 
# echo python3 $SCRIPT --file $dy50 --branch gmtSaMuon --label DYToLL_M-50_lut6_unscaled --unscale-l1-muon-pt True --lutversion 6 $ARGS
}

torun | parallel -v --joblog log -j 2 --eta