import ROOT
    
def format_histo(name, title, bins, start, end, color=ROOT.kBlack, **set_attrs):
    histo = ROOT.TH1F(name, title, bins, start, end)
    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetMarkerStyle(20)
    histo.Sumw2()

    for attr, value in set_attrs.items():
        setter = getattr(histo, f'Set{attr}', None)
        if setter is None: 
            print(f'[WARNING] unable to set attribute {attr} for TH1F')
            continue
        setter(histo, value)
    return histo


def format_histo2d(name, title, bins, start, end, bins2, start2, end2, color=ROOT.kBlack, **set_attrs):
    histo = ROOT.TH2F(name, title, bins, start, end, bins2, start2, end2)
    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetMarkerStyle(20)
    histo.Sumw2()

    for attr, value in set_attrs.items():
        setter = getattr(histo, f'Set{attr}', None)
        if setter is None: 
            print(f'[WARNING] unable to set attribute {attr} for TH2F')
            continue
        setter(histo, value)
    return histo