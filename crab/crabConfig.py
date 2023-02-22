from CRABClient.UserUtilities import config
config = config()

config.General.workArea        = 'ekoenig_Muon_Phase2'
config.General.requestName     = 'ekoenig_Muon_Phase2_{sample}'
config.General.transferOutputs = True
config.General.transferLogs    = False

config.JobType.pluginName  = 'Analysis'
config.JobType.psetName    = 'myconfig125OnlyRead.py'
# config.JobType.maxMemoryMB = 25
config.JobType.numCores    = 1

config.Data.inputDataset = '{das}'
config.Data.inputDBS = 'global'
config.Data.splitting = 'Automatic'
# config.Data.unitsPerJob = 25
# config.Data.totalUnits = 625
config.Data.outLFNDirBase = '/store/user/ekoenig/trigger/NTuples/Phase2/'
config.Data.publication = False

# config.Data.outputPrimaryDataset = 'DYToLL_M-10To50_TuneCP5_14TeV-pythia8'
config.Data.outputDatasetTag     = 'ekoenig_Muon_Phase2_{sample}'

config.Site.storageSite = 'T3_US_FNALLPC'