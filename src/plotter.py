import ROOT
import numpy as np
from array import array
from dataio import DataIO
import pandas as pd
import glob
from pathlib import Path
from PIL import Image


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
        self.table = ""
        self.table_df = None
        # Store objects so they persist
        self._objs = []
        # simple canvas counter to give unique canvas names
        self._canvas_count = 0

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
                'x_range': (1.0, 5000.0),
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

    def load_table(self, table_name):
        """
        Load a table by name.

        :param table_name: Name of the table to load.
        """
        # Verify table exists
        import os
        if not os.path.isfile(table_name):
            raise FileNotFoundError(f"Table file '{table_name}' not found.")
        self.table = table_name
        self.table_df = pd.read_csv(table_name)
        # Summarize loaded table
        print(f"Loaded table '{table_name}' with {len(self.table_df)} rows.")

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

    def plot_th2f(self, pad=None, bin_x_name=None, bin_y_name=None, cut="Weight", bin_rects=None, special_bin_rect=None):
        """
        Plot a TH2F histogram using two entries in plot_configs.

        :param pad: ROOT.TPad to draw on (optional)
        :param bin_x_name: key in plot_configs for the X-axis variable
        :param bin_y_name: key in plot_configs for the Y-axis variable
        :param cut: cut string for the tree draw
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
        self.tree.Draw(draw_cmd, cut, "COLZ")
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
        # --- Draw bin rectangles if provided ---
        if bin_rects:
            # get current canvas/pad to attach primitives if needed
            try:
                canvas = ROOT.gPad.GetCanvas()
            except Exception:
                canvas = None

            for irect, rect in enumerate(bin_rects):
                try:
                    xmin, xmax, ymin, ymax = rect
                except Exception:
                    # Skip invalid rect entries
                    continue
                # Reset xmax, ymax if it reaches beyond axis range
                if xmax > x_max:
                    xmax = x_max
                if ymax > y_max:
                    ymax = y_max
                box = ROOT.TBox(xmin, ymin, xmax, ymax)
                box.SetFillStyle(0)  # transparent

                box.SetLineColor(ROOT.kBlack)
                box.SetLineWidth(1)
                box.SetLineStyle(1)
                box.Draw("same")
                self._objs.append(box)
            # Draw the special bin rectangle if provided
            if special_bin_rect:
                try:
                    xmin, xmax, ymin, ymax = special_bin_rect
                except Exception:
                    pass
                else:
                    # Reset xmax, ymax if it reaches beyond axis range
                    if xmax > x_max:
                        xmax = x_max
                    if ymax > y_max:
                        ymax = y_max
                    box = ROOT.TBox(xmin, ymin, xmax, ymax)
                    box.SetFillStyle(0)  # transparent
                    box.SetLineColor(ROOT.kRed)
                    box.SetLineWidth(3)
                    box.SetLineStyle(1)
                    box.Draw("same")
                    self._objs.append(box)
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

    def plot_combo(self, plot_funcs, ncols=1, suptitle=None, output_name="combo_plot.png"):
        """
        plot_funcs: list of callables or tuples (callable, kwargs_dict)
        Each func should accept pad as a keyword argument.
        """
        n = len(plot_funcs)
        nrows = (n + ncols - 1) // ncols
        self._canvas_count += 1
        cname = f"combo_{self._canvas_count}"
        canvas = ROOT.TCanvas(cname, cname, 400*ncols, 400*nrows)
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
        out_path = self.data_io.get_output_dir() / output_name  
        print("Saving combo plot to:", out_path)
        canvas.SaveAs(str(out_path))

        return self._keep(canvas)

    def plot_bin_from_table(self, bin_number):
        """
        Plot 2D distributions for a specific bin from the loaded table.

        :param bin_number: The bin number (row index in the table)
        """
        if self.table_df is None:
            raise ValueError("Table not loaded. Use load_table() first.")

        if bin_number >= len(self.table_df):
            raise ValueError(f"Bin number {bin_number} out of range. Table has {len(self.table_df)} rows.")

        columns = self.table_df.columns
        row = self.table_df.iloc[bin_number]
        # Find unique prefaces for _min and _max
        prefaces_list = []
        for col in columns:
            if col.endswith('_min') and col[:-4] not in prefaces_list:
                prefaces_list.append(col[:-4])  # Remove '_min'

        
        


        if len(prefaces_list) < 2:
            raise ValueError("Need at least two variables with _min/_max columns.")

        # Mapping for variable names (e.g., Q -> Q2)
        name_mapping = {'Q': 'Q2'}

        # Create cut string based on the bin
        # Also, get subtable cut for first two variables
        subtable = self.table_df.copy()
        cuts = []
        special_bin_rect = []
        for pref in prefaces_list[:2]:
            mapped_name = name_mapping.get(pref, pref)
            min_val = row[f"{pref}_min"]
            max_val = row[f"{pref}_max"]
            special_bin_rect.append(min_val**2)
            special_bin_rect.append(max_val**2)
            subtable = subtable[(subtable[f"{pref}_min"] == min_val) & (subtable[f"{pref}_max"] == max_val)]
            cuts.append(f"{mapped_name} >= {min_val} && {mapped_name} <= {max_val}")

        cut_str = " && ".join(cuts)
        cut_str = "(" + cut_str + ") * Weight"
        # Plot functions for plot_combo
        plot_funcs = []

        # Define function to get unique rectangles for binning
        def _unique_rects_for(var_x, var_y, use_subtable=False):
            rects = []
            if use_subtable:
                for _, r in subtable.iterrows():
                    xmin = r[f"{var_x}_min"]
                    xmax = r[f"{var_x}_max"]
                    ymin = r[f"{var_y}_min"]
                    ymax = r[f"{var_y}_max"]
                    if (xmin, xmax, ymin, ymax) not in rects:
                        rects.append((xmin, xmax, ymin, ymax))
            else:
                for _, r in self.table_df.iterrows():
                    xmin = r[f"{var_x}_min"]
                    xmax = r[f"{var_x}_max"]
                    ymin = r[f"{var_y}_min"]**2 # Q--> Q2
                    ymax = r[f"{var_y}_max"]**2 # Q--> Q2
                    if (xmin, xmax, ymin, ymax) not in rects:
                        rects.append((xmin, xmax, ymin, ymax))
            return rects
        # Print the full subtable
        # First two variables
        var1, var2 = prefaces_list[0], prefaces_list[1]
        x1 = name_mapping.get(var1, var1)
        y1 = name_mapping.get(var2, var2)
        rects_12 = _unique_rects_for(var1, var2)
        plot_funcs.append(lambda pad=None, x=x1, y=y1, c="Weight", rects=rects_12: self.plot_th2f(pad=pad, bin_x_name=x, bin_y_name=y, cut=c, bin_rects=rects, special_bin_rect=special_bin_rect))

        # Last two variables
        var3, var4 = prefaces_list[-2], prefaces_list[-1]
        x2 = name_mapping.get(var3, var3)
        y2 = name_mapping.get(var4, var4)
        rects_34 = _unique_rects_for(var3, var4, use_subtable=True)
        plot_funcs.append(lambda pad=None, x=x2, y=y2, c=cut_str, rects=rects_34: self.plot_th2f(pad=pad, bin_x_name=x, bin_y_name=y, cut=c, bin_rects=rects))

        # Use plot_combo to display both plots
        suptitle = f"Bin {bin_number}: {x1} vs {y1} and {x2} vs {y2}"
        self.plot_combo(plot_funcs, ncols=2, suptitle=suptitle, output_name=f"bin_{bin_number}_plots.png")

    def make_bin_plots_gif(self, output_name: str = "bin_plots.gif", duration: float = 0.2):
        """
        Find all files matching `bin_*_plots.png` under `out_dir` (recursively) and make an animated GIF.

        :param output_name: Name of the output GIF file to write (will be placed inside out_dir)
        :param duration: Frame duration in seconds (default 0.2 == 200ms)
        :return: Path to the created GIF as a pathlib.Path
        """
        base = Path(self.data_io.get_output_dir())

        if not base.exists():
            raise FileNotFoundError(f"Output directory '{base}' does not exist")

        # Find matching files recursively
        pattern = "bin_*_plots.png"
        # Sort files naturally to handle non-zero-padded numbers
        import re
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]
        files = sorted([p for p in base.rglob(pattern)], key=natural_sort_key)

        if not files:
            raise FileNotFoundError(f"No files matching '{pattern}' found under '{base}'")

        images = [Image.open(f) for f in files]
        out_path = base / output_name

        # Save GIF using Pillow
        images[0].save(
            out_path,
            save_all=True,
            append_images=images[1:],
            duration=int(duration * 1000),  # Convert seconds to milliseconds
            loop=0
        )

        print(f"Created GIF with {len(images)} frames: {out_path}")
        return out_path
