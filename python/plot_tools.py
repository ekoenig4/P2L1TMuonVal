import functools, ROOT

class Sample:
    def __init__(self, tfname, xsec, total_events):
        self.tfname = tfname
        self.tf = ROOT.TFile.Open(tfname)
        self.xsec = xsec

        if isinstance(total_events, str):
            total_events = self.tf.Get(total_events).Integral()
        
        self.scale = xsec/total_events

    def Get(self, key):
        self.tf.cd()
        return self.tf.Get(key).Clone()

    def GetScaled(self, key):
        self.tf.cd()
        h = self.Get(key).Clone()
        h.Scale(self.scale)
        return h

class Dataset:
    def __init__(self, dataset, **kwargs):
        self.dataset = [ Sample(key, xsec, 'CountGenMuons') for key, xsec in dataset.items() ]
        self.__dict__.update(**kwargs)

    def Get(self, key):

        histos = [
            tf.GetScaled(key)
            for tf in self.dataset
        ]

        def histo_sum(h1, h2):
            h1_clone = h1.Clone()
            h2_clone = h2.Clone()
            h1_clone.Add(h2_clone)
            return h1_clone

        return functools.reduce(histo_sum, histos)

    def __getitem__(self, key):
        return self.dataset[key]