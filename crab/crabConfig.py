from CRABClient.UserUtilities import config
config = config()

config.General.requestName     = 'ekoenig_Muon_Phase2_DYToll_M-10To50'
config.General.workArea        = 'ekoenig_Muon_Phase2_DYToll_M-10To50'
config.General.transferOutputs = True
config.General.transferLogs    = False

config.JobType.pluginName  = 'Analysis'
config.JobType.psetName    = 'myconfig125OnlyRead.py'
# config.JobType.maxMemoryMB = 25
config.JobType.numCores    = 1

config.Data.inputDataset = '/DYToLL_M-10To50_TuneCP5_14TeV-pythia8/Phase2Fall22DRMiniAOD-PU200_Pilot_125X_mcRun4_realistic_v2-v2/GEN-SIM-DIGI-RAW-MINIAOD'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 25
config.Data.totalUnits = 625
config.Data.outLFNDirBase = '/store/user/ekoenig/trigger/NTuples/Phase2/'
config.Data.publication = False

# config.Data.outputPrimaryDataset = 'DYToLL_M-10To50_TuneCP5_14TeV-pythia8'
config.Data.outputDatasetTag     = 'ekoenig_Muon_Phase2_DYToll_M-10To50'

config.Site.storageSite = 'T3_US_FNALLPC'