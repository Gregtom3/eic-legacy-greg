#!/usr/bin/env ruby

Dir.chdir("submodules/epic-analysis") do
  system("ruby hpc/run-local-slurm-pipeline.rb --runcard ../../analysis/filippo/runcards/ep_piplus.yaml")
end
