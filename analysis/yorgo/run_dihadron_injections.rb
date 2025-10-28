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
config = {
  main_outdir:       "analysis/yorgo/injectout",
  file:              "out/BeAGLE.eHe3_pipluspiminus___epic.25.08.0_10x166/analysis.root",
  tree:              "dihadron_tree",
  energy:            "10x166",
  table:             "tables/x_only/AUT_average_PV20_EPIC_piplus_sqrts=28.636.txt",
  maxEntries:        10000,
  channel:           "Dihadron",
  eic_timeline:      "EarlyScience",
  target:            "Helium3",
  grid:              "X",
  n_injections:      1,
  extract_with_true: false,
  targetPolarization: 0.7,
  bins_per_slurm_job: 5
}

run_injection_workflow(config)