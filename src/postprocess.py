import os
import yaml
import pandas as pd

class PostProcessor:
    """
    A class for post-processing YAML files containing bin data from injection analysis.
    
    This class loads YAML files from a specified directory, extracts bin information,
    and provides methods to access the data as a pandas DataFrame or print summaries.
    """
    
    def __init__(self, directory):
        """
        Initialize the PostProcessor with a directory containing YAML files.
        
        Args:
            directory (str): Path to the directory containing YAML files with bin data
        """
        self.directory = directory
        self.bins = []
        self.df = None
        self.load_bins()
        self.create_dataframe()

    def load_bins(self):
        """
        Load bin data from all YAML files in the specified directory.
        
        This method scans the directory for .yaml files, parses them, and collects
        all job entries into self.bins. The bins are sorted by bin_index.
        """
        if not os.path.isdir(self.directory):
            print(f"Error: {self.directory} is not a valid directory")
            return

        yaml_files = [f for f in os.listdir(self.directory) if f.endswith('.yaml')]

        for yaml_file in yaml_files:
            file_path = os.path.join(self.directory, yaml_file)
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'jobs' in data:
                        self.bins.extend(data['jobs'])
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

        # Sort bins by bin_index
        self.bins.sort(key=lambda x: x['bin_index'])

    def create_dataframe(self):
        """
        Create a pandas DataFrame from the loaded bin data.
        
        The DataFrame is indexed by bin_index and contains all columns
        present in the YAML data (events, X_min, X_max, etc.).
        """
        if not self.bins:
            self.df = pd.DataFrame()
            return

        self.df = pd.DataFrame(self.bins)
        self.df.set_index('bin_index', inplace=True)

    def get_dataframe(self):
        """
        Get the pandas DataFrame containing all bin data.
        
        Returns:
            pd.DataFrame: DataFrame with bin data indexed by bin_index
        """
        return self.df

    def print(self):
        """
        Print the contents of the DataFrame.
        
        Displays the full pandas DataFrame with all bin data.
        """
        if self.df is None or self.df.empty:
            print("No data in DataFrame")
            return
        print("DataFrame contents:")
        print(self.df)
