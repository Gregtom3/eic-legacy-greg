import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

    def plot_bins(self):
        """
        Plot the bin data in a grid of subplots.

        Each subplot corresponds to a bin and shows data points with x error bars.
        A vertical dotted line represents the mean_extracted value with a red faded
        transparent 1-sigma error band.
        """
        if self.df is None or self.df.empty:
            print("No data to plot")
            return

        num_bins = len(self.df)
        num_cols = min(5, num_bins)  # Maximum 5 columns
        num_rows = (num_bins + num_cols - 1) // num_cols  # Calculate rows needed

        fig, axes = plt.subplots(num_rows, num_cols, figsize=(5 * num_cols, 4 * num_rows))
        axes = axes.flatten()  # Flatten in case of multiple rows

        for i, (bin_index, row) in enumerate(self.df.iterrows()):
            ax = axes[i]

            # Extract data for plotting
            all_extracted = row.get('all_extracted', [])
            all_errors = row.get('all_errors', [])
            mean_extracted = row.get('mean_extracted', 0)
            stddev_extracted = row.get('stddev_extracted', 0)

            if not all_extracted or not all_errors:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=12)
                ax.axis('off')
                continue

            y_values = np.arange(len(all_extracted))  # Spaced out y values

            # Plot data points with error bars
            point_alpha = 1 if len(all_extracted) < 50 else 0.5
            point_size = 50 if len(all_extracted) < 50 else 20
            ax.errorbar(all_extracted, y_values, xerr=all_errors, fmt='o', color="black", label='Data points', alpha=point_alpha, markersize=point_size)

            # Plot mean_extracted with 1-sigma error band
            ax.axvline(mean_extracted, color='blue', linestyle='dotted', label='Mean extracted')
            ax.fill_betweenx(y_values, mean_extracted - stddev_extracted, mean_extracted + stddev_extracted,
                             color='blue', alpha=0.2, label='1-sigma band')

            # Calculate error in the mean by hand
            n_points = len(all_extracted)
            if n_points > 0:
                error_in_mean = stddev_extracted / np.sqrt(n_points)
                ax.fill_betweenx(y_values, mean_extracted - error_in_mean, mean_extracted + error_in_mean,
                                 color='black', alpha=0.2, label='Error in mean')

            
            ax.set_title(f"Bin {bin_index}")
            ax.set_xlabel("Extracted Value")
            ax.set_ylabel("Trial Index")
            ax.legend()

        # Turn off unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].axis('off')

        plt.tight_layout()
        plt.savefig(os.path.join(self.directory, "asym_bin_extractions.png"))
