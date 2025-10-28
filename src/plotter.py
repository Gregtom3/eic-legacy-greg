import uproot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from io import StringIO


class BinningPlotter:
    """
    Load a TTree from a .root file and generate x-Q, z-pT, and combined plots.
    """
    def __init__(self, root_file, tree_name="tree"):
        self.root_file = root_file
        with uproot.open(root_file) as f:
            t = f[tree_name]
            arr = t.arrays(["X", "Q2", "Z", "PhPerp", "Weight"], library="np")
        self.X = arr["X"]
        self.Q2 = arr["Q2"]
        self.Z = arr["Z"]
        self.pT = arr["PhPerp"]
        self.W = arr["Weight"]
        self.Q = np.sqrt(self.Q2)

    @staticmethod
    def load_bin_table(csv_file):
        with open(csv_file, "r") as f:
            content = f.read()
        _, table = content.split("List of points \n")
        return pd.read_csv(StringIO(table))

    def get_bin(self, csv_file, bin_number):
        df = self.load_bin_table(csv_file)
        bins = df[["xMin", "xMax", "Qmin[GeV]", "Qmax[GeV]"]].drop_duplicates().to_numpy()
        if bin_number >= len(bins):
            raise ValueError(f"Bin index {bin_number} out of range 0-{len(bins)-1}")
        return bins[bin_number]

    def plot_xQ(self, ax, X_min=None, X_max=None, Q_min=None, Q_max=None):
        xbins = np.logspace(-4, 0, 50)
        Qbins = np.logspace(0, 2, 50)
        H, xe, qe = np.histogram2d(self.X, self.Q, bins=[xbins, Qbins], weights=self.W)
        mesh = ax.pcolormesh(xe, qe, H.T,
                             norm=mcolors.LogNorm(vmin=1, vmax=H.max()+1),
                             cmap="viridis")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("x")
        ax.set_ylabel("Q [GeV]")
        if X_min is not None:
            rect = mpatches.Rectangle((X_min, Q_min), X_max-X_min, Q_max-Q_min,
                                      fill=False, color="red", linewidth=2)
            ax.add_patch(rect)
        return mesh

    def plot_zpT(self, ax, X_min=None, X_max=None, Q_min=None, Q_max=None):
        if None in (X_min, X_max, Q_min, Q_max):
            mask = np.ones_like(self.X, dtype=bool)
        else:
            mask = (self.X > X_min) & (self.X < X_max) & (self.Q > Q_min) & (self.Q < Q_max)
        zbins = np.linspace(0.05, 1.1, 50)
        pTbins = np.linspace(-0.05, 3.0, 50)
        H2, ze, pe = np.histogram2d(self.Z[mask], self.pT[mask], bins=[zbins, pTbins], weights=self.W[mask])
        mesh = ax.pcolormesh(ze, pe, H2.T,
                             norm=mcolors.LogNorm(vmin=1, vmax=H2.max()+1),
                             cmap="viridis")
        ax.set_xlabel("z")
        ax.set_ylabel("pT [GeV]")
        return mesh

    def plot_combo(self, plot_funcs, figsize=(10, 5), suptitle=None, **kwargs):
        """
        plot_funcs: list of callables, each f(ax, **kwargs)
        kwargs are passed to each plotting function
        """
        fig, axes = plt.subplots(1, len(plot_funcs), figsize=figsize)
        if len(plot_funcs) == 1:
            axes = [axes]
        meshes = []
        for ax, func in zip(axes, plot_funcs):
            meshes.append(func(ax, **kwargs))
            plt.colorbar(meshes[-1], ax=ax, pad=0.01)
        if suptitle:
            fig.suptitle(suptitle)
        plt.tight_layout()
        plt.show()
        return axes
