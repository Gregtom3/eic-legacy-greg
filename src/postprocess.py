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
        self.terms = self.collect_directory_terms()

    def collect_directory_terms(self):
        """
        Collect terms from the directory path for metadata purposes.

        e.g. directory = analysis/yorgo/injectout/Dihadron/10x166/EarlyScience/Helium3/X
        would yield terms = ['Dihadron', '10x166', 'EarlyScience', 'Helium3', 'X']

        Returns:    
            dict: A dictionary with keys 'channel', 'energy', 'eic_timeline', 'target', 'grid'
        """
        parts = os.path.normpath(self.directory).split(os.sep)
        term_data = parts[-5:]  # Get the last 5 parts of the path
        terms = {
            'channel': term_data[0],
            'energy': term_data[1],
            'eic_timeline': term_data[2],
            'target': term_data[3],
            'grid': term_data[4]
        }
        return terms

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

    def save_to_csv(self):
        """
        Save the DataFrame to a CSV file.
        """
        if self.df is None or self.df.empty:
            print("No data to save")
            return

        output_path = os.path.join(self.directory, "ALL_INJECTION_RESULTS.csv")
        self.df.to_csv(output_path)
        print(f"[INFO] Saved DataFrame to {output_path}")

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

        fig, axes = plt.subplots(num_rows, num_cols, figsize=(6 * num_cols, 5 * num_rows))
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
            point_size = 6 if len(all_extracted) < 50 else 3
            ax.errorbar(all_extracted, y_values, xerr=all_errors, fmt='o', color="black", label='Data points (w/ exp. error)', alpha=point_alpha, markersize=point_size)

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

        fig.suptitle(", ".join([f"{k}: {v}" for k, v in self.terms.items()]), fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(self.directory, "asym_bin_extractions.png"))
        print("[INFO] Saved asym_bin_extractions.png")
        plt.show()

    def plot_asymmetry(self):
        """
        Plot the asymmetry as a function of bin index.

        The x-axis represents the bin index, and the y-axis represents the asymmetry.
        A scatter plot shows the reconstructed injected asymmetry (mean_extracted).
        Two error bars are included:
        1. Standard error bars with caps for the mean of "all_errors".
        2. A red transparent band for the standard error of the mean.
        """
        if self.df is None or self.df.empty:
            print("No data to plot")
            return

        bin_indices = self.df.index
        mean_extracted = self.df['mean_extracted']
        all_errors_mean = self.df['all_errors'].apply(lambda x: np.mean(x) if isinstance(x, list) else 0)
        stddev_extracted = self.df['stddev_extracted']
        n_points = self.df['all_extracted'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        true_asymmetry = self.df['injected']

        # Calculate standard error of the mean
        error_in_mean = stddev_extracted / np.sqrt(n_points)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Scatter plot for mean_extracted
        ax.errorbar(bin_indices, mean_extracted, yerr=all_errors_mean, fmt='o', capsize=5, label='Expected EIC AUT w/ Error', color='black')

        # Red transparent band for standard error of the mean
        ax.fill_between(bin_indices, mean_extracted - error_in_mean, mean_extracted + error_in_mean,
                         color='red', alpha=0.2, label='Monte Carlo Statistical Uncertainty in AUT')

        # Plot true asymmetry line
        ax.plot(bin_indices, true_asymmetry, color='blue', linestyle='dashed', label='True Injected AUT')

        # Labels and legend
        ax.set_title(", ".join([f"{k}: {v}" for k, v in self.terms.items()]))
        ax.set_xlabel("Bin Index")
        ax.set_ylabel("Asymmetry")
        ax.set_xticks(bin_indices)  # Ensure x-axis labels are integers
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)  # Add x-y grid
        ax.legend()

        plt.tight_layout()
        plt.savefig(os.path.join(self.directory, "asymmetry_vs_bin_index.png"))
        print("[INFO] Saved asymmetry_vs_bin_index.png")
        plt.show()
