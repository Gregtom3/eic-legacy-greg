#!/usr/bin/env ruby
require 'fileutils'
require 'time'
require 'csv'
require 'set'

module InjectionWorkflow
    def run_injection_workflow(cfg)
    outDir = "#{cfg[:main_outdir]}/#{cfg[:channel]}/#{cfg[:energy]}/#{cfg[:eic_timeline]}/#{cfg[:target]}/#{cfg[:grid]}/"
    FileUtils.mkdir_p(outDir) unless Dir.exist?(outDir)
    
    # Delete yaml files in outDir
    Dir.glob("#{outDir}/*.yaml").each { |f| File.delete(f) }

    timestamp = Time.now.strftime("%Y%m%d_%H%M%S")
    job_dir = "#{outDir}/slurm/#{timestamp}"
    FileUtils.mkdir_p(job_dir)

    # parse grid list
    grid_list = cfg[:grid].split(",").map(&:strip)
    allowed_grids = %w[X Q Z PhPerp]
    invalid = grid_list.reject { |g| allowed_grids.include?(g) }
    raise "Invalid grid values: #{invalid.join(", ")}" if invalid.any?

    # Determine unique bins
    unique_bins = Set.new
    CSV.foreach(cfg[:table], col_sep: ",", headers: true) do |row|
        key = grid_list.flat_map do |g|
        ["#{g}_min", "#{g}_max"].map { |col| row[col].to_f }
        end
        unique_bins.add(key)
    end

    bins = unique_bins.size
    puts "Detected #{bins} unique bins for grid #{grid_list.join(",")}."

    # Logging
    log_file = File.join(outDir, "injection_log.txt")
    File.open(log_file, 'a') do |log|
        log.puts "===== Injection Run at #{timestamp} ====="
        cfg.each { |k, v| log.puts "#{k}: #{v}" }
        log.puts "bins: #{bins}"
        log.puts "=====================================\n"
    end

    slurm_scripts = []

    # Create SLURM scripts
    (0...bins).each_slice(cfg[:bins_per_slurm_job]) do |bin_group|
        job_name = "inj_#{bin_group.first}_to_#{bin_group.last}_#{cfg[:energy]}"
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
        f.puts "  --file #{cfg[:file]} \\"
        f.puts "  --tree #{cfg[:tree]} \\"
        f.puts "  --energy #{cfg[:energy]} \\"
        f.puts "  --table #{cfg[:table]} \\"
        f.puts "  --outDir #{outDir} \\"
        f.puts "  --maxEntries #{cfg[:maxEntries]} \\"
        f.puts "  --channel #{cfg[:channel]} \\"
        f.puts "  --eic_timeline #{cfg[:eic_timeline]} \\"
        f.puts "  --target #{cfg[:target]} \\"
        f.puts "  --grid #{cfg[:grid]} \\"
        f.puts "  --n_injections #{cfg[:n_injections]} \\"
        f.puts "  --extract_with_true #{cfg[:extract_with_true]} \\"
        f.puts "  --targetPolarization #{cfg[:targetPolarization]} \\"
        f.puts "  --bin_index_start #{bin_group.first} \\"
        f.puts "  --bin_index_end #{bin_group.last} \\"
        f.puts "  --outFilename bins_#{bin_group.first}_to_#{bin_group.last}.yaml"
        end

        slurm_scripts << script_path
        puts "Created SLURM script: #{script_path}"
    end

    puts "\nSLURM job scripts located in: #{job_dir}\n"

    # Prompt for execution mode
    loop do
        puts "Choose execution mode:"
        puts "1: Submit batch jobs (outside eic-shell)"
        puts "2: Run directly (inside eic-shell)"
        puts "3: Cancel"
        print "> "
        case STDIN.gets.strip
        when "1"
        slurm_scripts.each { |s| system("sbatch #{s}") }
        puts "Submitted #{slurm_scripts.size} jobs."
        break
        when "2"
        puts "Running locally..."
        (0...bins).each_slice(cfg[:bins_per_slurm_job]) do |bin_group|
            cmd = [
            "./submodules/tmd-eic-ana/bin/inject",
            "--file", cfg[:file],
            "--tree", cfg[:tree],
            "--energy", cfg[:energy],
            "--table", cfg[:table],
            "--outDir", outDir,
            "--maxEntries", cfg[:maxEntries].to_s,
            "--channel", cfg[:channel],
            "--eic_timeline", cfg[:eic_timeline],
            "--target", cfg[:target],
            "--grid", cfg[:grid],
            "--n_injections", cfg[:n_injections].to_s,
            "--extract_with_true", cfg[:extract_with_true].to_s,
            "--targetPolarization", cfg[:targetPolarization].to_s,
            "--outFilename", "bins_#{bin_group.first}_to_#{bin_group.last}.yaml",
            "--bin_index_start", bin_group.first.to_s,
            "--bin_index_end",   bin_group.last.to_s
            ]
            puts "\nRunning: #{cmd.join(' ')}\n"
            system(cmd.join(' '))
        end
        puts "All local injections completed."
        break
        when "3"
        puts "Cancelled."
        break
        else
        puts "Invalid input."
        end
    end
    end
end
