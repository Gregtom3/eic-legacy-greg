#!/usr/bin/env ruby
require 'fileutils'
require 'time'
require 'csv'
require 'set'
require_relative "../../src/injection_workflow"
include InjectionWorkflow

# Environment setup
ENV['LD_LIBRARY_PATH'] = "#{ENV['HOME']}/.local/lib64:#{ENV['LD_LIBRARY_PATH']}"

# Configuration Parameters
# For the eHe3 dihadron injections
config = {
  main_outdir:       "analysis/yorgo/injectout",
  file:              "out/BeAGLE.eHe3_pipluspiminus___epic.25.08.0_10x166/analysis.root",
  tree:              "dihadron_tree",
  energy:            "10x166",
  table:             "analysis/yorgo/tables/x_binning_table.csv",
  maxEntries:        100_000_000,
  channel:           "Dihadron",
  eic_timeline:      "EarlyScience",
  target:            "Helium3",
  grid:              "X",
  n_injections:      1_000,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 1
}

run_injection_workflow(config)

# Configuration Parameters
# For the ep dihadron injections <EARLY SCIENCE>
config = {
  main_outdir:       "analysis/yorgo/injectout",
  file:              "out/PYTHIA8.ep_pipluspiminus___epic.25.08.0_10x100/analysis.root",
  tree:              "dihadron_tree",
  energy:            "10x100",
  table:             "analysis/yorgo/tables/x_binning_table.csv",
  maxEntries:        100_000_000,
  channel:           "Dihadron",
  eic_timeline:      "EarlyScience",
  target:            "Proton",
  grid:              "X",
  n_injections:      1_000,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 1
}

run_injection_workflow(config)

# For the ep dihadron injections <FULL>
config = {
  main_outdir:       "analysis/yorgo/injectout",
  file:              "out/PYTHIA8.ep_pipluspiminus___epic.25.08.0_10x100/analysis.root",
  tree:              "dihadron_tree",
  energy:            "10x100",
  table:             "analysis/yorgo/tables/x_binning_table.csv",
  maxEntries:        100_000_000,
  channel:           "Dihadron",
  eic_timeline:      "Full",
  target:            "Proton",
  grid:              "X",
  n_injections:      1_000,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 1
}

run_injection_workflow(config)

# Configuration Parameters
# For the 4d ep dihadron injections
config = {
  main_outdir:       "analysis/yorgo/injectout",
  file:              "out/PYTHIA8.ep_pipluspiminus___epic.25.08.0_10x100/analysis.root",
  tree:              "dihadron_tree",
  energy:            "10x100",
  table:             "analysis/yorgo/tables/xQ2ZMh_binning_table.csv",
  maxEntries:        100_000_000,
  channel:           "Dihadron",
  eic_timeline:      "EarlyScience",
  target:            "Proton",
  grid:              "X,Q,Z,Mh",
  n_injections:      10,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 100
}

run_injection_workflow(config)
