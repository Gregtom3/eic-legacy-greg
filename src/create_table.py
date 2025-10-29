#!/usr/bin/env python3
import sys
import numpy as np
import pandas as pd
import itertools


def main():
    if len(sys.argv) != 2:
        print("Usage: python create_table.py <function_name>")
        sys.exit(1)

    function_name = sys.argv[1]

    # Check if the function exists in globals
    if function_name in globals() and callable(globals()[function_name]):
        print(f"Executing function: {function_name}")
        globals()[function_name]()
    else:
        print(f"Error: Function '{function_name}' not found or not callable")
        sys.exit(1)



def generate_table(list_of_bin_edges, list_of_bin_names, aut_value):
    """
    Generate a pandas DataFrame with binning information.
    
    Args:
        list_of_bin_edges: List of arrays, each containing bin edges for a dimension
        list_of_bin_names: List of dimension names ('X', 'Q2', 'Z', 'PhPerp')
        aut_value: AUT value to assign
    
    Returns:
        pd.DataFrame: DataFrame with binning information
    """
    global_bin_names = ['X', 'Q2', 'Z', 'PhPerp']
    
    if len(list_of_bin_edges) != len(list_of_bin_names):
        print("Error: Length of bin edges and bin names must be the same")
        return None

    for name in list_of_bin_names:
        if name not in global_bin_names:
            print(f"Error: Bin name '{name}' is not allowed")
            return None
    
    # Create all combinations of bin indices
    bin_indices = [range(len(edges) - 1) for edges in list_of_bin_edges]
    combinations = list(itertools.product(*bin_indices))
    
    # Calculate total number of bins
    total_bins = len(combinations)
    
    # Determine AUT value per bin
    if aut_value == total_bins:
        aut_per_bin = aut_value / total_bins
    else:
        aut_per_bin = 0
    
    # Create DataFrame
    data = []
    for combo in combinations:
        row = {
            'itar': 1,
            'ihad': 1,
            'X_min': 0,
            'X_max': 9999,
            'Q_min': 0,
            'Q_max': 9999,
            'Z_min': 0,
            'Z_max': 9999,
            'PhPerp_min': 0,
            'PhPerp_max': 9999,
            'AUT': aut_per_bin
        }
        
        # Set the actual bin values for provided dimensions
        for i, name in enumerate(list_of_bin_names):
            bin_idx = combo[i]
            edges = list_of_bin_edges[i]
            if name == 'X':
                row['X_min'] = edges[bin_idx]
                row['X_max'] = edges[bin_idx + 1]
            elif name == 'Q2':
                row['Q_min'] = edges[bin_idx]
                row['Q_max'] = edges[bin_idx + 1]
            elif name == 'Z':
                row['Z_min'] = edges[bin_idx]
                row['Z_max'] = edges[bin_idx + 1]
            elif name == 'PhPerp':
                row['PhPerp_min'] = edges[bin_idx]
                row['PhPerp_max'] = edges[bin_idx + 1]
        
        data.append(row)
    
    df = pd.DataFrame(data)
    return df
    


def yorgo_x_table():
    """
    Generate a table with X binning for Yorgo's analysis.
    """
    xbins = np.array([
        1.58e-05,
        2.51e-05,
        3.98e-05,
        6.31e-05,
        0.0001,
        0.0001585,
        0.0002512,
        0.0003981,
        0.000631,
        0.001,
        0.0015849,
        0.0025119,
        0.0039811,
        0.0063096,
        0.01,
        0.0158489,
        0.0251189,
        0.0398107,
        0.0630957,
        0.1,
        0.1584893,
        0.2511886,
        0.3981072,
        0.6309573,
        1.0
    ])
    
    # Generate table with X binning only
    df = generate_table([xbins], ['X'], aut_value=0)
    if df is not None:
        print("Generated Yorgo X table:")
        print(df.head())
        df.to_csv("analysis/yorgo/tables/x_binning_table.csv", index=False)


if __name__ == "__main__":
    main()