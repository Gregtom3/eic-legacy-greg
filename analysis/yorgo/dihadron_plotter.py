import sys
from pathlib import Path
sys.path.append("src")
from plotter import Plotter
from dataio import DataIO

def main():
    root_file = "out/BeAGLE.eHe3_pipluspiminus___epic.25.08.0_10x166/analysis.root"
    treename = "dihadron_tree"
    data_io = DataIO(root_file, treename)
    plotter = Plotter(data_io)
    plotter.plot_combo([plotter.plot_xQ, plotter.plot_zpT],
                       ncols=2,
                       suptitle="Dihadron Simulation Plots")

if __name__ == "__main__":
    main()