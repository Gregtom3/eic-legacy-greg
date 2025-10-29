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
# For the e+p 5x41 PYTHIA8 dataset
config_5x41 = {
  main_outdir:       "analysis/filippo/injectout",
  file:              "out/PYTHIA8.ep_piplus___epic.25.08.0_5x41/analysis.root",
  tree:              "tree",
  energy:            "5x41",
  table:             "analysis/filippo/tables/x_only/AUT_average_PV20_EPIC_piplus_sqrts=28.636.txt",
  maxEntries:        500_000_000,
  channel:           "Hadron",
  eic_timeline:      "Full",
  target:            "Proton",
  grid:              "X",
  n_injections:      1000,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 1
}

run_injection_workflow(config_5x41)

# Configuration Parameters
# For the e+p 10x100 PYTHIA8 dataset
config_10x100 = {
  main_outdir:       "analysis/filippo/injectout",
  file:              "out/PYTHIA8.ep_piplus___epic.25.08.0_10x100/analysis.root",
  tree:              "tree",
  energy:            "10x100",
  table:             "analysis/filippo/tables/x_only/AUT_average_PV20_EPIC_piplus_sqrts=63.246.txt",
  maxEntries:        500_000_000,
  channel:           "Hadron",
  eic_timeline:      "Full",
  target:            "Proton",
  grid:              "X",
  n_injections:      1_000,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 1
}

run_injection_workflow(config_10x100)

# Configuration Parameters
# For the e+p 18x275 PYTHIA8 dataset
config_18x275 = {
  main_outdir:       "analysis/filippo/injectout",
  file:              "out/PYTHIA8.ep_piplus___epic.25.08.0_18x275/analysis.root",
  tree:              "tree",
  energy:            "18x275",
  table:             "analysis/filippo/tables/x_only/AUT_average_PV20_EPIC_piplus_sqrts=140.712.txt",
  maxEntries:        500_000_000,
  channel:           "Hadron",
  eic_timeline:      "Full",
  target:            "Proton",
  grid:              "X",
  n_injections:      1_000,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 1
}

run_injection_workflow(config_18x275)