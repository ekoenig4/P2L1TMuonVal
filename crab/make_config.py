import os 
import subprocess

dataset_list = [
    # dict(
    #     sample="DYToll_M-10To50",
    #     das="/DYToLL_M-10To50_TuneCP5_14TeV-pythia8/Phase2Fall22DRMiniAOD-PU200_Pilot_125X_mcRun4_realistic_v2-v2/GEN-SIM-DIGI-RAW-MINIAOD"
    # ),
    dict(
        sample="DYToll_M-50",
        das="/DYToLL_M-50_TuneCP5_14TeV-pythia8/Phase2Fall22DRMiniAOD-PU200_125X_mcRun4_realistic_v2-v1/GEN-SIM-DIGI-RAW-MINIAOD"
    )
]

template_config = os.path.join( os.path.dirname(__file__), 'crabConfig.py' )
with open(template_config, 'r') as tmp:
    template_config = tmp.read()

if not os.path.exists('configs/'):
    os.mkdir('configs/')

for dataset in dataset_list:
    print("Creating config for ")
    print(dataset)
    config_name = f'configs/crabConfig_{dataset["sample"]}.py'
    with open(config_name,'w') as config:
        config.write(template_config.format(**dataset))
    print("Submitting")
    subprocess.run(["crab","submit",config_name], check=True, shell=True)