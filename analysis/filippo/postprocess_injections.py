import sys
from pathlib import Path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))
from postprocess import PostProcessor


DIRECTORIES = ["analysis/filippo/injectout/Hadron/5x41/Full/Proton/X",
               "analysis/filippo/injectout/Hadron/10x100/Full/Proton/X",
               "analysis/filippo/injectout/Hadron/18x275/Full/Proton/X"]

def main():
    for DIRECTORY in DIRECTORIES:
        processor = PostProcessor(DIRECTORY)
        processor.print()
        processor.plot_bins()
        processor.plot_asymmetry()
        processor.save_to_csv()

if __name__ == "__main__":
    main()
