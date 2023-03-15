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

