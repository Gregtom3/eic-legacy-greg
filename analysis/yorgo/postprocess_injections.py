import sys
from pathlib import Path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))
from postprocess import PostProcessor


DIRECTORY = "analysis/yorgo/injectout/Dihadron/10x166/EarlyScience/Helium3/X"

def main():
    processor = PostProcessor(DIRECTORY)
    processor.print()

if __name__ == "__main__":
    main()
