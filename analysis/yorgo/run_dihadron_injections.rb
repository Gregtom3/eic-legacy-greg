#!/usr/bin/env ruby
require 'fileutils'
require 'time'
require 'csv'
require 'set'

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
n_injections      = 1
extract_with_true = false
targetPolarization = 0.7
bins_per_slurm_job = 5      # bins grouped into each slurm job

####################### Program logic #######################
#############################################################
outDir = "#{MAINOUTDIR}/#{channel}/#{energy}/#{eic_timeline}/#{target}/#{grid}/"

# Ensure output directory exists
unless Dir.exist?(outDir)
  puts "Output directory #{outDir} does not exist. Creating it now."
  FileUtils.mkdir_p(outDir)
end

# Set up job directory with timestamp
timestamp = Time.now.strftime("%Y%m%d_%H%M%S")
job_dir = "#{outDir}/slurm/#{timestamp}"
FileUtils.mkdir_p(job_dir)

log_file = File.join(outDir, "injection_log.txt")

# Parse grid list (may be comma-separated)
grid_list = grid.split(",").map(&:strip)
allowed_grids = %w[X Q Z PhPerp]
invalid = grid_list.reject { |g| allowed_grids.include?(g) }
if invalid.any?
  STDERR.puts "ERROR: Invalid grid values: #{invalid.join(", ")}"
  STDERR.puts "Allowed: #{allowed_grids.join(", ")}"
  exit 1
end

# ------- READ THE TABLE & DETERMINE UNIQUE BINS -------
unique_bins = Set.new

begin
  CSV.foreach(table, col_sep: ",", headers: true) do |row|
    key = []
    grid_list.each do |g|
      min_col = "#{g}_min"
      max_col = "#{g}_max"
      unless row.headers.include?(min_col) && row.headers.include?(max_col)
        STDERR.puts "ERROR: Table missing required columns #{min_col} or #{max_col}"
        exit 1
      end
      key << row[min_col].to_f
      key << row[max_col].to_f
    end
    unique_bins.add(key)
  end
rescue Errno::ENOENT
  STDERR.puts "ERROR: Table file not found: #{table}"
  exit 1
end

bins = unique_bins.size
puts "Detected #{bins} unique #{grid_list.join(',')} bins from: #{table}"


# ANSI color helper
def color(text)
  "\e[32m#{text}\e[0m"
end

# Strip ANSI color codes
def strip_colors(text)
  text.gsub(/\e\[[0-9;]*m/, '')
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
  #{color("Number of Bins:")} #{bins}
  #{color("Bins per Job:")} #{bins_per_slurm_job}
  #{color("Number of Injections:")} #{n_injections}
  #{color("Extract with True:")} #{extract_with_true}
  #{color("Target Polarization:")} #{targetPolarization}
  #{color("Output Directory:")} #{outDir}
  ========================================
  Starting injection process...

  LOG

  puts header
  log.write(strip_colors(header))
end

slurm_scripts = []

# ------- CREATE JOB SCRIPTS -------
(0...bins).each_slice(bins_per_slurm_job) do |bin_group|
  job_name = "inj_#{bin_group.first}_to_#{bin_group.last}_#{energy}"
  script_path = File.join(job_dir, "slurm_#{job_name}.sh")

  File.open(script_path, "w") do |f|
    f.puts "#!/bin/bash"
    f.puts "#SBATCH --job-name=#{job_name}"
    f.puts "#SBATCH --output=#{job_dir}/%x_%j.out"
    f.puts "#SBATCH --error=#{job_dir}/%x_%j.err"
    f.puts "#SBATCH --account=eic"
    f.puts "#SBATCH --partition=production"
    f.puts "#SBATCH --cpus-per-task=2"
    f.puts "#SBATCH --mem-per-cpu=4G"
    f.puts "#SBATCH --time=24:00:00"
    f.puts
    f.puts "srun ./submodules/tmd-eic-ana/bin/inject \\"
    f.puts "  --file #{file} \\"
    f.puts "  --tree #{tree} \\"
    f.puts "  --energy #{energy} \\"
    f.puts "  --table #{table} \\"
    f.puts "  --outDir #{MAINOUTDIR}/#{channel}/#{energy}/#{eic_timeline}/#{target}/#{grid}/ \\"
    f.puts "  --maxEntries #{maxEntries} \\"
    f.puts "  --channel #{channel} \\"
    f.puts "  --eic_timeline #{eic_timeline} \\"
    f.puts "  --target #{target} \\"
    f.puts "  --grid #{grid} \\"
    f.puts "  --n_injections #{n_injections} \\"
    f.puts "  --extract_with_true #{extract_with_true} \\"
    f.puts "  --targetPolarization #{targetPolarization} \\"
    f.puts "  --bin_index_start #{bin_group.first} \\"
    f.puts "  --outFilename bins_#{bin_group.first}_to_#{bin_group.last}.yaml \\"
    f.puts "  --bin_index_end #{bin_group.last}"
  end

  slurm_scripts << script_path
  puts "Created: #{script_path}"
end

puts "\nAll job scripts written to: #{job_dir}\n\n"

# ------- SUBMIT? -------
loop do
  puts "Choose an option:"
  puts "1: Submit to slurm (ONLY WORKS OUTSIDE OF EIC-SHELL)"
  puts "2: Run in terminal (ONLY WORKS WITHIN EIC-SHELL)"
  puts "3: Cancel"
  print "Enter 1, 2, or 3: "
  choice = STDIN.gets.strip

  case choice
  when "1"
    slurm_scripts.each { |s| system("sbatch #{s}") }
    puts "Submitted #{slurm_scripts.size} jobs."
    break
  when "2"
    puts "Running injections in terminal..."
    (0...bins).each_slice(bins_per_slurm_job) do |bin_group|
      cmd = [
        "./submodules/tmd-eic-ana/bin/inject",
        "--file", file,
        "--tree", tree,
        "--energy", energy,
        "--table", table,
        "--outDir", "#{MAINOUTDIR}/#{channel}/#{energy}/#{eic_timeline}/#{target}/#{grid}/",
        "--maxEntries", maxEntries.to_s,
        "--channel", channel,
        "--eic_timeline", eic_timeline,
        "--target", target,
        "--grid", grid,
        "--n_injections", n_injections.to_s,
        "--extract_with_true", extract_with_true.to_s,
        "--targetPolarization", targetPolarization.to_s,
        "--bin_index_start", bin_group.first.to_s,
        "--bin_index_end", bin_group.last.to_s
      ]
      puts "Running: #{cmd.join(' ')}"
      system(cmd.join(' '))
    end
    puts "All injections completed."
    break
  when "3"
    puts "Cancelled."
    break
  else
    puts "Invalid choice. Please enter 1, 2, or 3."
  end
end
