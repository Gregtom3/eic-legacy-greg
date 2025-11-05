import sys
from pathlib import Path
sys.path.append("src")
from plotter import Plotter
from dataio import DataIO

def main():
    root_files = [
        "out/PYTHIA8.ep_pipluspiminus___epic.25.08.0_10x100/analysis.root",
        "out/BeAGLE.eHe3_pipluspiminus___epic.25.08.0_10x166/analysis.root",
    ]
    treename = "dihadron_tree"
    
    for i, root_file in enumerate(root_files):
        print(f"Processing file {i+1}/{len(root_files)}: {root_file}")
        data_io = DataIO(root_file, treename)
        plotter = Plotter(data_io)
        plotter.load_table("analysis/yorgo/tables/xQ2ZMh_binning_table.csv")
        # Extract filename for plot title
        filename = Path(root_file).parent.name
        suptitle = f"Dihadron Simulation Plots - {filename}"
        
        plotter.plot_combo([
            (plotter.plot_th2f, {'bin_x_name': 'X', 'bin_y_name': 'Q2'}),
            (plotter.plot_th2f, {'bin_x_name': 'Z', 'bin_y_name': 'PhPerp'}),
            (plotter.plot_th1f, {'bin_name': 'Z'}),
            (plotter.plot_th1f, {'bin_name': 'PhPerp'}),
            (plotter.plot_th1f, {'bin_name': 'Mh'}),
            (plotter.plot_th1f, {'bin_name': 'XF1'}),
            (plotter.plot_th1f, {'bin_name': 'XF2'}),
            (plotter.plot_th1f, {'bin_name': 'PhiRperp'}),
            (plotter.plot_th1f, {'bin_name': 'ThetaCOM'}),
        ], ncols=3, suptitle=suptitle)

        # Loop over all x-Q2 bins in the table
        for i in range(100):
            plotter.plot_bin_from_table(i*100)

        # Make a gif from the x-Q2 bin plots
        plotter.make_bin_plots_gif()
        
if __name__ == "__main__":
    main()