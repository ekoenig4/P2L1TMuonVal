import ROOT
import awkward as ak
import numpy as np
import os 
from array import array

def save_canvas(canvas, fname, fmt=['png']):
    dirname = os.path.dirname(fname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    for _fmt in fmt:
        canvas.SaveAs(f"{fname}.{_fmt}")

def tset(tobj, **attrs):
    for attr, value in attrs.items():
        setter = getattr(tobj, f'Set{attr}', None)
        if setter is None: 
            print(f'[WARNING] unable to set attribute {attr} for {type(tobj)}')
            continue
        if not isinstance(value, (tuple, list)): value = [value]
        setter(*value)
    return tobj


    
def format_histo_varbin(name, title, bins, color=ROOT.kBlack, **set_attrs):
    if isinstance(bins, tuple):
        histo = ROOT.TH1F(name, title, *bins)
    elif isinstance(bins, np.ndarray):
        bins = array('d', bins)
        histo = ROOT.TH1F(name, title, len(bins)-1, bins)

    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetMarkerStyle(20)
    histo.Sumw2()

    return tset(histo, **set_attrs)
    
def format_histo(name, title, bins, start, end, color=ROOT.kBlack, **set_attrs):
    histo = ROOT.TH1F(name, title, bins, start, end)
    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetMarkerStyle(20)
    histo.Sumw2()

    return tset(histo, **set_attrs)


def format_histo2d(name, title, bins, start, end, bins2, start2, end2, color=ROOT.kBlack, **set_attrs):
    histo = ROOT.TH2F(name, title, bins, start, end, bins2, start2, end2)
    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetMarkerStyle(20)
    histo.Sumw2()

    return tset(histo, **set_attrs)


def fill_th1(th1, x_array, weights=None):
    if weights is None:
        weights = ak.ones_like(x_array)

    x_array = ak.flatten(x_array, axis=None).to_numpy()
    weights = ak.flatten(weights, axis=None).to_numpy()

    for (x, w) in zip(x_array, weights): th1.Fill(x,w)


# def fill_th1_array(th1, array, weights=None):
#     array = ak.flatten(array, axis=None).to_numpy()

#     n_bins = th1.GetNbinsX()
#     bins = [ th1.GetBinLowEdge(i) for i in range(n_bins+3) ]
#     array = np.clip(array, bins[0], bins[-1])

#     counts, _ = np.histogram(array, bins=bins, weights=weights)
#     weights2 = weights**2 if weights is not None else None
#     errors, _ = np.histogram(array, bins=bins, weights=weights2)
#     errors = np.sqrt(errors)

#     th1.SetEntries(len(array))
#     for i, (count, error) in enumerate(zip(counts,errors)):
#         th1.SetBinContent(i, count)
#         th1.SetBinError(i, error)

def fill_th2(th2, x_array, y_array, weights=None):
    if weights is None:
        weights = ak.ones_like(x_array)

    x_array = ak.flatten(x_array, axis=None).to_numpy()
    y_array = ak.flatten(y_array, axis=None).to_numpy()
    weights = ak.flatten(weights, axis=None).to_numpy()

    for (x, y, w) in zip(x_array, y_array, weights): th2.Fill(x,y,w)


# def fill_th2_array(th2, x_array, y_array, weights=None):
#     x_array = ak.flatten(x_array, axis=None).to_numpy()
#     y_array = ak.flatten(y_array, axis=None).to_numpy()

#     n_xbins = th2.GetNbinsX()
#     xbins = [ th2.GetXaxis().GetBinLowEdge(i) for i in range(n_xbins+3) ]

#     n_ybins = th2.GetNbinsY()
#     ybins = [ th2.GetYaxis().GetBinLowEdge(i) for i in range(n_ybins+3) ]
#     x_array = np.clip(x_array, xbins[0], xbins[-1])
#     y_array = np.clip(y_array, ybins[0], ybins[-1])

#     counts, _, _ = np.histogram2d(x_array, y_array, bins=(xbins, ybins), weights=weights)
#     weights2 = weights**2 if weights is not None else None
#     errors, _, _ = np.histogram2d(x_array, y_array, bins=(xbins, ybins), weights=weights2)
#     errors = np.sqrt(errors)

#     th2.SetEntries(len(x_array))
#     for i in range(n_xbins+2):
#         for j in range(n_ybins+2):
#             th2.SetBinContent(i, j, counts[i,j])
#             th2.SetBinError(i, j, errors[i,j])
