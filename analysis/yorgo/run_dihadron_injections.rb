#!/usr/bin/env ruby
require 'fileutils'

# Environment setup
ENV['LD_LIBRARY_PATH'] = "#{ENV['HOME']}/.local/lib64:#{ENV['LD_LIBRARY_PATH']}"

# REPOSITORY-WIDE Configuration Parameters
MAINOUTDIR = "analysis/yorgo/injectout"

# Configuration Parameters
file              = "out/BeAGLE.eHe3_pipluspiminus___epic.25.08.0_10x166/analysis.root"
tree              = "dihadron_tree"
energy            = "10x166"
table             = "tables/x_only/AUT_average_PV20_EPIC_piplus_sqrts=28.636.txt"
maxEntries        = 10000
channel           = "Dihadron"
eic_timeline      = "EarlyScience"
target            = "Helium3"
grid              = "X"
n_injections      = 10
extract_with_true = false
targetPolarization = 0.7

outDir = "#{MAINOUTDIR}/#{channel}/#{energy}/#{eic_timeline}/#{target}/#{grid}/"

# Ensure output directory exists
unless Dir.exist?(outDir)
  puts "Output directory #{outDir} does not exist. Creating it now."
  FileUtils.mkdir_p(outDir)
end

log_file = File.join(outDir, "injection_log.txt")

# ANSI color helper
def color(text)
  "\e[32m#{text}\e[0m"
end

File.open(log_file, 'w') do |log|
  header = <<~LOG
  ========================================
  Injection Script Execution Log
  ========================================
  #{color("File:")} #{file}
  #{color("Tree:")} #{tree}
  #{color("Energy:")} #{energy}
  #{color("Table:")} #{table}
  #{color("Max Entries:")} #{maxEntries}
  #{color("Channel:")} #{channel}
  #{color("EIC Timeline:")} #{eic_timeline}
  #{color("Target:")} #{target}
  #{color("Grid:")} #{grid}
  #{color("Number of Injections:")} #{n_injections}
  #{color("Extract with True:")} #{extract_with_true}
  #{color("Target Polarization:")} #{targetPolarization}
  #{color("Output Directory:")} #{outDir}
  ========================================
  Starting injection process...

  LOG

  puts header
  log.write(header)
end

sleep 2

cmd = [
  "./submodules/tmd-eic-ana/bin/inject",
  "--file", file,
  "--tree", tree,
  "--energy", energy,
  "--outDir", outDir,
  "--table", table,
  "--maxEntries", maxEntries.to_s,
  "--channel", channel,
  "--eic_timeline", eic_timeline,
  "--target", target,
  "--grid", grid,
  "--n_injections", n_injections.to_s,
  "--extract_with_true", extract_with_true.to_s,
  "--targetPolarization", targetPolarization.to_s
]

# Run command and tee output to log
IO.popen(cmd, err: [:child, :out]) do |pipe|
  File.open(log_file, 'a') do |log|
    pipe.each do |line|
      print line
      log.write(line)
    end
  end
end
