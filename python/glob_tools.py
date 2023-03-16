import subprocess, os
from glob import glob as local_glob

default_url = 'root://cmseos.fnal.gov/'

def store_glob(filepath, url=default_url):
    cmd = ['eos', url, 'ls', filepath]
    stdout = subprocess.run(
        [' '.join(cmd)], shell=True, capture_output=True).stdout.decode("utf-8")
    dirlist = stdout.strip().split('\n')
    
    path = os.path.dirname(filepath)
    return [f'{url}{path}/{d}' for d in dirlist]

def glob(filepath, url=default_url):
    filelist = local_glob(filepath)
    if any(filelist):
        return filelist

    filelist = store_glob(filepath, url)
    return filelist

def get_filelist(files, url=default_url):
    if not isinstance(files, list): files = [files]
    filelist = []
    for filepath in files:
        if filepath.endswith('.txt'):
            with open(filepath, 'r') as f:
                for _file in f.readlines():
                    filelist += glob(_file, url)
        else:
            filelist += glob(filepath, url)

    return filelist
