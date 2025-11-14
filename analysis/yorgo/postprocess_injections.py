import sys
from pathlib import Path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))
from postprocess import PostProcessor


DIRECTORIES = ["analysis/yorgo/injectout/Dihadron/10x166/EarlyScience/Helium3/X",
               "analysis/yorgo/injectout/Dihadron/10x100/EarlyScience/Proton/X",
               "analysis/yorgo/injectout/Dihadron/10x100/EarlyScience/Proton/X,Q,Z,Mh"]

def main():
    for DIRECTORY in DIRECTORIES:
        processor = PostProcessor(DIRECTORY)
        processor.print()
        if "X,Q,Z,Mh" not in DIRECTORY:
            processor.plot_bins()
            processor.plot_asymmetry()
        processor.save_to_csv()

if __name__ == "__main__":
    main()
