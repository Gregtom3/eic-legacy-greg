import sys
from pathlib import Path
sys.path.append("src")
from plotter import Plotter
from dataio import DataIO

def main():
    root_file = "out/PYTHIA8.ep_piplus___epic.25.08.0_5x41/analysis.root"
    treename = "tree"
    data_io = DataIO(root_file, treename)
    plotter = Plotter(data_io)
    plotter.plot_combo([
        plotter.plot_xQ,  
        plotter.plot_zpT,
        (plotter.plot_th1f, {'bin_name': 'Z'}),
        (plotter.plot_th1f, {'bin_name': 'PhPerp'}),
        (plotter.plot_th1f, {'bin_name': 'Mh'}),
        (plotter.plot_th1f, {'bin_name': 'XF'}),
        (plotter.plot_th1f, {'bin_name': 'MX'}),
        (plotter.plot_th1f, {'bin_name': 'PhiH'}),
        (plotter.plot_th1f, {'bin_name': 'Depol_SIDIS'}),
    ], ncols=3, suptitle="Single Hadron SIDIS Plots")


if __name__ == "__main__":
    main()