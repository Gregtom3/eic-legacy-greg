import ROOT
import numpy as np
from array import array
from dataio import DataIO

def style_hist(hist):
    ROOT.gPad.SetLeftMargin(0.17)
    ROOT.gPad.SetRightMargin(0.17)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.12)
    ROOT.gPad.SetTicks(1, 1)

    if isinstance(hist, ROOT.TH2):
        ROOT.gPad.SetGridx(1)
        ROOT.gPad.SetGridy(1)

    hist.GetXaxis().SetTitleSize(0.07)
    hist.GetYaxis().SetTitleSize(0.07)
    hist.GetZaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(0.75)
    hist.GetYaxis().SetTitleOffset(1.2)
    hist.SetLineColor(1)
    hist.SetLineWidth(2)
    return hist


class Plotter:
    """
    ROOT-only plotting class that prevents histogram garbage collection.
    """
    def __init__(self, data_io: DataIO):
        self.data_io = data_io
        self.file = ROOT.TFile.Open(data_io.filepath)
        self.tree = self.file.Get(data_io.treename)

        # Store objects so they persist
        self._objs = []

    def _keep(self, obj):
        """Keep reference so ROOT doesn't delete it."""
        self._objs.append(obj)
        return obj

    def plot_xQ(self, pad=None):
        if pad:
            pad.cd()

        x_edges = array('d', np.logspace(-4, 0, 50+1))
        q_edges = array('d', np.logspace(0, 2, 50+1))

        h = ROOT.TH2F("h_xQ", "",
                      len(x_edges)-1, x_edges,
                      len(q_edges)-1, q_edges)
        draw_cmd = "sqrt(Q2):X >> h_xQ"
        self.tree.Draw(draw_cmd, "Weight", "COLZ")
        h.SetDirectory(0)

        ROOT.gPad.SetLogx()
        ROOT.gPad.SetLogy()
        ROOT.gPad.SetLogz()

        h.GetXaxis().SetTitle("x")
        h.GetYaxis().SetTitle("Q [GeV]")

        style_hist(h)
        return self._keep(h)

    def plot_zpT(self, pad=None):
        if pad:
            pad.cd()

        z_edges = array('d', np.linspace(0, 28, 50+1))
        pT_edges = array('d', np.linspace(0, 100, 50+1))
        h = ROOT.TH2F("h_zpT", "",
                      len(z_edges)-1, z_edges,
                      len(pT_edges)-1, pT_edges)
        draw_cmd = "PhPerp:Z >> h_zpT"
        self.tree.Draw(draw_cmd, "Weight", "COLZ")
        h.SetDirectory(0)

        ROOT.gPad.SetLogz()

        h.GetXaxis().SetTitle("z")
        h.GetYaxis().SetTitle("p_{T} [GeV]")

        style_hist(h)
        return self._keep(h)

    def plot_combo(self, plot_funcs, ncols=1, suptitle=None):
        n = len(plot_funcs)
        nrows = (n + ncols - 1) // ncols

        canvas = ROOT.TCanvas("combo", "combo", 400*ncols, 400*nrows)
        canvas.Divide(ncols, nrows)

        for i, func in enumerate(plot_funcs, start=1):
            canvas.cd(i)
            ROOT.gStyle.SetOptStat(0)
            func(pad=ROOT.gPad)

        if suptitle:
            canvas.SetTitle(suptitle)

        # Save + persist
        out_path = self.data_io.get_output_dir() / "combo_plot.png"
        print("Saving combo plot to:", out_path)
        canvas.SaveAs(str(out_path))

        return self._keep(canvas)
