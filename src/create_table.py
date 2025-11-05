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
            'Mh_min': 0,
            'Mh_max': 9999,
            'AUT': aut_value
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
            elif name == 'Mh':
                row['Mh_min'] = edges[bin_idx]
                row['Mh_max'] = edges[bin_idx + 1]

        data.append(row)
    
    df = pd.DataFrame(data)
    return df
    


def yorgo_x_table():
    """
    Generate a table with X binning for Yorgo's analysis.
    """
    xbins = np.array([
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
    df = generate_table([xbins], ['X'], aut_value=0.1)
    if df is not None:
        print("Generated Yorgo X table:")
        print(df)
        df.to_csv("analysis/yorgo/tables/x_binning_table.csv", index=False)


def yorgo_xQ2ZMh_table():
    import uproot
    from scipy import stats

    # =====================================================
    # Load ROOT file and read specified branches
    # =====================================================
    filename = "out/PYTHIA8.ep_pipluspiminus___epic.25.08.0_10x100/analysis.root" 
    # filename = "out/BeAGLE.eHe3_pipluspiminus___epic.25.08.0_10x166/analysis.root"
    tree_name = "dihadron_tree"

    with uproot.open(filename) as f:
        tree = f[tree_name]
        X = tree["X"].array(library="np")
        Q2 = tree["Q2"].array(library="np")
        Z = tree["Z"].array(library="np")
        Mh = tree["Mh"].array(library="np")
        Weight = tree["Weight"].array(library="np")

    df = pd.DataFrame({
        "X": X,
        "Q2": Q2,
        "Z": Z,
        "Mh": Mh,
        "Weight": Weight
    })

    # =====================================================
    # Helper function: weighted-equal binning
    # =====================================================
    def weighted_equal_bins(values, weights, n_bins):
        """Return bin edges so that total weight per bin is roughly equal."""
        if len(values) == 0:
            return None
        sorter = np.argsort(values)
        sorted_vals = values[sorter]
        sorted_weights = weights[sorter]
        cumsum = np.cumsum(sorted_weights)
        total = cumsum[-1]
        targets = np.linspace(0, total, n_bins + 1)
        edges = [sorted_vals[0]]
        for tw in targets[1:-1]:
            idx = np.searchsorted(cumsum, tw)
            edges.append(sorted_vals[idx])
        edges.append(sorted_vals[-1])
        return np.array(edges)

    # =====================================================
    # Hierarchical adaptive binning
    # =====================================================
    N_X, N_Q2, N_Z, N_Mh = 10, 10, 10, 10
    all_bin_weights = []
    records = []  # for CSV export

    # 1. Top-level X binning
    X_edges = weighted_equal_bins(df["X"].to_numpy(), df["Weight"].to_numpy(), N_X)

    for iX in range(N_X):
        X_low, X_high = X_edges[iX], X_edges[iX+1]
        df_X = df[(df["X"] >= X_low) & (df["X"] < X_high)]
        if len(df_X) == 0:
            continue

        # 2. Q² bins inside this X bin
        Q2_edges = weighted_equal_bins(df_X["Q2"].to_numpy(), df_X["Weight"].to_numpy(), N_Q2)
        if Q2_edges is None:
            continue

        for iQ2 in range(N_Q2):
            Q2_low, Q2_high = Q2_edges[iQ2], Q2_edges[iQ2+1]
            df_Q2 = df_X[(df_X["Q2"] >= Q2_low) & (df_X["Q2"] < Q2_high)]
            if len(df_Q2) == 0:
                continue

            # 3. Z bins inside this (X, Q²) bin
            Z_edges = weighted_equal_bins(df_Q2["Z"].to_numpy(), df_Q2["Weight"].to_numpy(), N_Z)
            if Z_edges is None:
                continue

            for iZ in range(N_Z):
                Z_low, Z_high = Z_edges[iZ], Z_edges[iZ+1]
                df_Z = df_Q2[(df_Q2["Z"] >= Z_low) & (df_Q2["Z"] < Z_high)]
                if len(df_Z) == 0:
                    continue

                # 4. Mh bins inside this (X, Q², Z) bin
                Mh_edges = weighted_equal_bins(df_Z["Mh"].to_numpy(), df_Z["Weight"].to_numpy(), N_Mh)
                if Mh_edges is None:
                    continue

                for iMh in range(N_Mh):
                    Mh_low, Mh_high = Mh_edges[iMh], Mh_edges[iMh+1]
                    df_Mh = df_Z[(df_Z["Mh"] >= Mh_low) & (df_Z["Mh"] < Mh_high)]
                    total_w = df_Mh["Weight"].sum()
                    all_bin_weights.append(total_w)

                    # record for CSV
                    records.append({
                        "itar": 1,
                        "ihad": 1,
                        "X_min": X_low,
                        "X_max": X_high,
                        "Q_min": np.sqrt(Q2_low),
                        "Q_max": np.sqrt(Q2_high),
                        "Z_min": Z_low,
                        "Z_max": Z_high,
                        "Mh_min": Mh_low,
                        "Mh_max": Mh_high,
                        "AUT": 0.1
                    })

    # =====================================================
    # Summarize total bin weights
    # =====================================================
    all_bin_weights = np.array(all_bin_weights)
    all_bin_weights = all_bin_weights[~np.isnan(all_bin_weights)]

    if len(all_bin_weights) == 0:
        print("No bins with events found.")
    else:
        smallest = np.sort(all_bin_weights)[:5]
        largest = np.sort(all_bin_weights)[-5:]
        mean = np.mean(all_bin_weights)
        std = np.std(all_bin_weights)
        median = np.median(all_bin_weights)
        mode_val = stats.mode(np.round(all_bin_weights, 6), keepdims=False).mode

        print("\n================ BIN WEIGHT SUMMARY ================")
        print(f"Total number of bins: {len(all_bin_weights)}")
        print("\n5 smallest weights:")
        print(smallest)
        print("\n5 largest weights:")
        print(largest)
        print(f"\nMean weight:   {mean:.6e}")
        print(f"Std. dev:      {std:.6e}")
        print(f"Median weight: {median:.6e}")
        print(f"Mode weight:   {mode_val:.6e}")
        print("====================================================")

    # =====================================================
    # Save binning scheme to CSV
    # =====================================================
    output_csv = "analysis/yorgo/tables/xQ2ZMh_binning_table.csv"
    df_bins = pd.DataFrame(records)
    df_bins.to_csv(output_csv, index=False)

    print(f"\nBinning scheme saved to: {output_csv}")
    print(f"Total rows written: {len(df_bins)}")


if __name__ == "__main__":
    main()
