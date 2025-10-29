import sys
from pathlib import Path
sys.path.append("src")
from plotter import Plotter
from dataio import DataIO

def main():
    files = [
        "out/PYTHIA8.ep_piplus___epic.25.08.0_5x41/analysis.root",
        "out/PYTHIA8.ep_piplus___epic.25.08.0_10x100/analysis.root",
        "out/PYTHIA8.ep_piplus___epic.25.08.0_18x275/analysis.root"
    ]
    treename = "tree"
    max_Q2 = [1000, 1000, 1000] # GeV^2
    for root_file in files:
        data_io = DataIO(root_file, treename)
        plotter = Plotter(data_io)
        # Extract the dataset name for the title
        dataset_name = root_file.split('/')[-2]  # e.g., 'PYTHIA8.ep_piplus___epic.25.08.0_5x41'
        plotter.update_plot_config('Q2', {'x_range': (1, max_Q2[files.index(root_file)])})
        plotter.plot_combo([
            (plotter.plot_th2f, {'bin_x_name': 'X', 'bin_y_name': 'Q2'}),
            (plotter.plot_th2f, {'bin_x_name': 'Z', 'bin_y_name': 'PhPerp'}),
            (plotter.plot_th1f, {'bin_name': 'Y'}),
            (plotter.plot_th1f, {'bin_name': 'W'}),
            (plotter.plot_th1f, {'bin_name': 'Z'}),
            (plotter.plot_th1f, {'bin_name': 'PhPerp'}),
            (plotter.plot_th1f, {'bin_name': 'xF'}),
            (plotter.plot_th1f, {'bin_name': 'PhiH'}),
            (plotter.plot_th1f, {'bin_name': 'Depol_SIDIS'}),
        ], ncols=3, suptitle=f"Single Hadron SIDIS Plots - {dataset_name}")


if __name__ == "__main__":
    main()