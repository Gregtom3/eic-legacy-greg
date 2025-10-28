import ROOT
import numpy as np
from array import array
from dataio import DataIO

def style_hist(hist):
    ROOT.gPad.SetLeftMargin(0.21)
    ROOT.gPad.SetRightMargin(0.17)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.21)
    ROOT.gPad.SetTicks(1, 1)

    if isinstance(hist, ROOT.TH2):
        ROOT.gPad.SetGridx(1)
        ROOT.gPad.SetGridy(1)
    else:
        hist.SetLineWidth(3)
    hist.GetXaxis().SetTitleSize(0.07)
    hist.GetYaxis().SetTitleSize(0.07)
    hist.GetZaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.05)
    hist.GetYaxis().SetTitleOffset(1.5)
    hist.GetXaxis().SetNdivisions(505)
    hist.SetLineColor(1)
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

        # Configuration dict for TH1F plots
        self.plot_configs = {
            'X': {
                'branch_name': 'X',
                'x_title': 'x',
                'y_title': 'Counts',
                'x_range': (1e-4, 1.0),
                'n_bins': 100,
                'log_x': True,
                'log_y': True
            },
            'Q2': {
                'branch_name': 'Q2',
                'x_title': 'Q^{2} [GeV^{2}]',
                'y_title': 'Counts',
                'x_range': (1.0, 1000.0),
                'n_bins': 100,
                'log_x': True,
                'log_y': True
            },
            'Z': {
                'branch_name': 'Z',
                'x_title': 'z',
                'y_title': 'Counts',
                'x_range': (0.0, 1.1),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'PhPerp': {
                'branch_name': 'PhPerp',
                'x_title': 'p_{T} [GeV]',
                'y_title': 'Counts',
                'x_range': (0.0, 5.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'Y': {
                'branch_name': 'Y',
                'x_title': 'Y',
                'y_title': 'Counts',
                'x_range': (0.0, 1.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'W': {
                'branch_name': 'W',
                'x_title': 'W [GeV]',
                'y_title': 'Counts',
                'x_range': (0.0, 200.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'XF1': {
                'branch_name': 'XF1',
                'x_title': 'x-Feynman (h_{1})',
                'y_title': 'Counts',
                'x_range': (-0.1, 1.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'XF2': {
                'branch_name': 'XF2',
                'x_title': 'x-Feynman (h_{2})',
                'y_title': 'Counts',
                'x_range': (-0.1, 1.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'xF': {
                'branch_name': 'xF',
                'x_title': 'x-Feynman',
                'y_title': 'Counts',
                'x_range': (-0.1, 1.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'Mh': {
                'branch_name': 'Mh',
                'x_title': 'M_{h} [GeV]',
                'y_title': 'Counts',
                'x_range': (0.0, 5.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'PhiH': {
                'branch_name': 'PhiH',
                'x_title': '#phi_{h} [rad]',
                'y_title': 'Counts',
                'x_range': (np.pi, np.pi),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'PhiRperp': {
                'branch_name': 'PhiRperp',
                'x_title': '#phi_{R#perp} [rad]',
                'y_title': 'Counts',
                'x_range': (np.pi, np.pi),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'PhiRT': {
                'branch_name': 'PhiRT',
                'x_title': '#phi_{R_{T}} [rad]',
                'y_title': 'Counts',
                'x_range': (np.pi, np.pi),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'ThetaCOM': {
                'branch_name': 'ThetaCOM',
                'x_title': '#Theta [rad]',
                'y_title': 'Counts',
                'x_range': (0.0, np.pi),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            },
            'Depol_SIDIS': {
                'branch_name': 'Depol1',
                'x_title': 'Depolarization Factor',
                'y_title': 'Counts',
                'x_range': (0, 1.0),
                'n_bins': 100,
                'log_x': False,
                'log_y': False
            }
        }

    def update_plot_config(self, bin_name, config_updates):
        """
        Update or add configuration for a specific bin_name in plot_configs.

        :param bin_name: The name of the bin (e.g., 'X', 'Q2')
        :param config_updates: Dict of updates to apply (e.g., {'x_title': 'New Title', 'log_x': False})
        """
        if bin_name not in self.plot_configs:
            self.plot_configs[bin_name] = {}
        self.plot_configs[bin_name].update(config_updates)

    def _keep(self, obj):
        """Keep reference so ROOT doesn't delete it."""
        self._objs.append(obj)
        return obj
        
    def plot_th2f(self, pad=None, bin_x_name=None, bin_y_name=None):
        """
        Plot a TH2F histogram using two entries in plot_configs.

        :param pad: ROOT.TPad to draw on (optional)
        :param bin_x_name: key in plot_configs for the X-axis variable
        :param bin_y_name: key in plot_configs for the Y-axis variable
        """

        # --- Validate configs ---
        if bin_x_name not in self.plot_configs:
            raise ValueError(f"X-axis bin '{bin_x_name}' not found in plot_configs.")
        if bin_y_name not in self.plot_configs:
            raise ValueError(f"Y-axis bin '{bin_y_name}' not found in plot_configs.")

        cfg_x = self.plot_configs[bin_x_name]
        cfg_y = self.plot_configs[bin_y_name]

        branch_x = cfg_x.get('branch_name', bin_x_name)
        branch_y = cfg_y.get('branch_name', bin_y_name)

        x_min, x_max = cfg_x['x_range']
        y_min, y_max = cfg_y['x_range']
        nx = cfg_x['n_bins']
        ny = cfg_y['n_bins']

        log_x = cfg_x['log_x']
        log_y = cfg_y['log_y']
        # (We treat log_z automatically below)

        # --- Create binning ---
        if log_x:
            x_bins = array('d', np.logspace(np.log10(x_min), np.log10(x_max), nx+1))
        else:
            x_bins = array('d', np.linspace(x_min, x_max, nx+1))

        if log_y:
            y_bins = array('d', np.logspace(np.log10(y_min), np.log10(y_max), ny+1))
        else:
            y_bins = array('d', np.linspace(y_min, y_max, ny+1))

        # --- Create histogram ---
        hist_name = f"h_{bin_x_name}_vs_{bin_y_name}"
        h = ROOT.TH2F(hist_name, "",
                       len(x_bins)-1, x_bins,
                       len(y_bins)-1, y_bins)


        if pad:
            pad.cd()

        # --- Draw tree data ---
        draw_cmd = f"{branch_y}:{branch_x} >> {hist_name}"
        self.tree.Draw(draw_cmd, "Weight", "COLZ")
        h.SetDirectory(0)
        # --- Log scales ---
        if log_x:
            ROOT.gPad.SetLogx()
        if log_y:
            ROOT.gPad.SetLogy()
        ROOT.gPad.SetLogz()  # Always useful for 2D counts

        # --- Style ---
        h.GetXaxis().SetTitle(cfg_x['x_title'])
        h.GetYaxis().SetTitle(cfg_y['x_title'])

        style_hist(h)
        h.Draw("COLZ")
    
        return self._keep(h)

    def plot_th1f(self, pad=None, bin_name=None):
        """
        Plot a TH1F histogram for the specified bin_name using configuration from plot_configs.
        """
        if bin_name not in self.plot_configs:
            raise ValueError(f"Bin name '{bin_name}' not found in plot_configs.")

        config = self.plot_configs[bin_name]
        branch_name = config.get('branch_name', bin_name) # Actual branch name in TTree
        x_title = config['x_title']
        y_title = config['y_title']
        x_min, x_max = config['x_range']
        n_bins = config['n_bins']
        log_x = config['log_x']
        log_y = config['log_y']

        if pad:
            pad.cd()

        hist_name = f"h_{bin_name}"
        if log_x:
            bin_edges = array('d', np.logspace(np.log10(x_min), np.log10(x_max), n_bins+1))
            h = ROOT.TH1F(hist_name, "", n_bins, bin_edges)
        else:
            h = ROOT.TH1F(hist_name, "", n_bins, x_min, x_max)
        draw_cmd = f"{branch_name} >> {hist_name}"
        self.tree.Draw(draw_cmd, "Weight", "goff")
        h.SetDirectory(0)

        if log_x:
            ROOT.gPad.SetLogx()
        if log_y:
            ROOT.gPad.SetLogy()

        h.GetXaxis().SetTitle(x_title)
        h.GetYaxis().SetTitle(y_title)

        style_hist(h)
        h.Draw("hist")
        return self._keep(h)

    def plot_combo(self, plot_funcs, ncols=1, suptitle=None):
        """
        plot_funcs: list of callables or tuples (callable, kwargs_dict)
        Each func should accept pad as a keyword argument.
        """
        n = len(plot_funcs)
        nrows = (n + ncols - 1) // ncols

        canvas = ROOT.TCanvas("combo", "combo", 400*ncols, 400*nrows)
        canvas.Divide(ncols, nrows)

        for i, item in enumerate(plot_funcs, start=1):
            canvas.cd(i)
            ROOT.gStyle.SetOptStat(0)
            if callable(item):
                item(pad=ROOT.gPad)
            elif isinstance(item, tuple) and len(item) == 2:
                func, kwargs = item
                func(pad=ROOT.gPad, **kwargs)
            else:
                raise ValueError("plot_funcs items must be callables or (callable, kwargs_dict) tuples")

        if suptitle:
            canvas.SetTitle(suptitle)

        # Save + persist
        out_path = self.data_io.get_output_dir() / "combo_plot.png"
        print("Saving combo plot to:", out_path)
        canvas.SaveAs(str(out_path))

        return self._keep(canvas)
