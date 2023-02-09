import awkward as ak
import numpy as np
from tqdm import tqdm 
from typing import Callable

def unzip_records(records):
    return {field: array for field, array in zip(records.fields, ak.unzip(records))}

def merge_records(*records, depth_limit=1):
    merged = dict()
    for record in records:
        merged.update( unzip_records(record) )
    return ak.zip(merged, depth_limit=depth_limit)

def variable_collection(records, prefix, sep="", keepname=False):
    collection_branches = list(
        filter(lambda branch: branch.startswith(prefix+sep), records.fields))
    branches = records[collection_branches]
    if keepname: return branches

    branches = {
        field.replace(prefix+sep,""):branches[field]
        for field in collection_branches
    }
    return ak.zip(branches, depth_limit=1)

def get_dphi(phi_1, phi_2):
    dphi = phi_2 - phi_1
    dphi = ak.where( dphi >= np.pi, dphi - 2.0*np.pi, dphi)
    dphi = ak.where( dphi < -np.pi, dphi + 2.0*np.pi, dphi)
    return dphi

def get_deta(eta_1, eta_2):
    deta = eta_2 - eta_1 
    return deta

def get_dr(eta_1, phi_1, eta_2, phi_2):
    deta = get_deta(eta_1, eta_2)
    dphi = get_dphi(phi_1, phi_2)
    return np.sqrt(deta**2 + dphi**2)

def get_obj_dr(obj_1, obj_2, eta='Eta', phi='Phi'):
    eta_1, phi_1 = ak.unzip(obj_1[[eta, phi]])
    eta_2, phi_2 = ak.unzip(obj_2[[eta, phi]])
    return get_dr(eta_1, phi_1, eta_2, phi_2)

def fill_th1(th1, array, weights=None):
    array = ak.flatten(array, axis=None).to_numpy()
    for value in array: th1.Fill(value)

def fill_th1_array(th1, array, weights=None):
    array = ak.flatten(array, axis=None).to_numpy()

    n_bins = th1.GetNbinsX()
    bins = [ th1.GetBinLowEdge(i) for i in range(n_bins+3) ]
    array = np.clip(array, bins[0], bins[-1])

    counts, _ = np.histogram(array, bins=bins, weights=weights)
    weights2 = weights**2 if weights is not None else None
    errors, _ = np.histogram(array, bins=bins, weights=weights2)
    errors = np.sqrt(errors)

    th1.SetEntries(len(array))
    for i, (count, error) in enumerate(zip(counts,errors)):
        th1.SetBinContent(i, count)
        th1.SetBinError(i, error)

def fill_th2(th2, x_array, y_array, weights=None):
    x_array = ak.flatten(x_array, axis=None).to_numpy()
    y_array = ak.flatten(y_array, axis=None).to_numpy()
    for x_value, y_value in zip(x_array, y_array): th2.Fill(x_value, y_value)

def fill_th2_array(th2, x_array, y_array, weights=None):
    x_array = ak.flatten(x_array, axis=None).to_numpy()
    y_array = ak.flatten(y_array, axis=None).to_numpy()

    n_xbins = th2.GetNbinsX()
    xbins = [ th2.GetXaxis().GetBinLowEdge(i) for i in range(n_xbins+3) ]

    n_ybins = th2.GetNbinsY()
    ybins = [ th2.GetYaxis().GetBinLowEdge(i) for i in range(n_ybins+3) ]
    x_array = np.clip(x_array, xbins[0], xbins[-1])
    y_array = np.clip(y_array, ybins[0], ybins[-1])

    counts, _, _ = np.histogram2d(x_array, y_array, bins=(xbins, ybins), weights=weights)
    weights2 = weights**2 if weights is not None else None
    errors, _, _ = np.histogram2d(x_array, y_array, bins=(xbins, ybins), weights=weights2)
    errors = np.sqrt(errors)

    th2.SetEntries(len(x_array))
    for i in range(n_xbins+2):
        for j in range(n_ybins+2):
            th2.SetBinContent(i, j, counts[i,j])
            th2.SetBinError(i, j, errors[i,j])
