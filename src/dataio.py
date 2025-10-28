from pathlib import Path

class DataIO:
    def __init__(self, filepath, treename):
        self.filepath = filepath
        self.treename = treename

    def get_file_subdir(self):
        return Path(self.filepath).parent

    def get_output_dir(self):
        return self.get_file_subdir() 