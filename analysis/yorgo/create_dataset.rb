#!/usr/bin/env ruby

Dir.chdir("submodules/epic-analysis") do
  system("ruby hpc/run-local-slurm-pipeline.rb --runcard ../../analysis/yorgo/runcards/eHe3_10x166_pipluspiminus.yaml")
  system("ruby hpc/run-local-slurm-pipeline.rb --runcard ../../analysis/yorgo/runcards/ep_10x100_pipluspiminus.yaml")
end

puts "=========================== Pipeline completed ==========================="
puts "Run the following scripts **OUTSIDE** the eic-shell environment:"
puts "  bash /w/hallb-scshelf2102/clas12/users/gmat/eic/eic-legacy-greg/submodules/epic-analysis/hpc/project_scripts/run-PYTHIA8.ep_pipluspiminus.sh"
puts "  bash /w/hallb-scshelf2102/clas12/users/gmat/eic/eic-legacy-greg/submodules/epic-analysis/hpc/project_scripts/run-BeAGLE.eHe3_pipluspiminus.sh"