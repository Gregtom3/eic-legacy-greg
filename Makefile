# Makefile for setting up the eic-shell and building submodules

EIC_SHELL_DIR := eic-shell
EIC_SHELL_URL := https://raw.githubusercontent.com/eic/eic-shell/main/eic-shell

.PHONY: all setup clean build-submodules

all: setup build-submodules

setup:
	@echo "Setting up eic-shell..."
	@mkdir -p $(EIC_SHELL_DIR)
	@curl -o $(EIC_SHELL_DIR)/eic-shell $(EIC_SHELL_URL)
	@chmod +x $(EIC_SHELL_DIR)/eic-shell
	@echo "eic-shell setup complete."

build-submodules:
	@echo "Building submodules..."
	@cd submodules/tmd-eic-ana && make
	@cd submodules/eicQuickSim && make
	@echo "Building epic-analysis in eic-shell..."
	@$(EIC_SHELL_DIR)/eic-shell -c "cd submodules/epic-analysis && source environ.sh && make"
	@echo "All submodules built successfully."

clean:
	@echo "Cleaning up eic-shell directory..."
	@rm -rf $(EIC_SHELL_DIR)
	@echo "Cleanup complete."