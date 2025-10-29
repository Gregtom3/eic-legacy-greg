import sys
from pathlib import Path
sys.path.append("src")
from plotter import Plotter
from dataio import DataIO

def main():
    root_files = [
        "out/BeAGLE.eHe3_pipluspiminus___epic.25.08.0_10x166/analysis.root",
        "out/PYTHIA8.ep_pipluspiminus___epic.25.08.0_10x100/analysis.root"
    ]
    treename = "dihadron_tree"
    
    for i, root_file in enumerate(root_files):
        print(f"Processing file {i+1}/{len(root_files)}: {root_file}")
        data_io = DataIO(root_file, treename)
        plotter = Plotter(data_io)
        
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

if __name__ == "__main__":
    main()