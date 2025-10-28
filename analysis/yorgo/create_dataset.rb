#!/usr/bin/env ruby

Dir.chdir("submodules/epic-analysis") do
  system("ruby hpc/run-local-slurm-pipeline.rb --runcard ../../analysis/yorgo/runcards/eHe3_10x166_pipluspiminus.yaml")
  system("ruby hpc/run-local-slurm-pipeline.rb --runcard ../../analysis/yorgo/runcards/ep_10x100_pipluspiminus.yaml")
end
