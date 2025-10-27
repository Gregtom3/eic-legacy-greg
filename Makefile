# Makefile for setting up the eic-shell and building submodules

EIC_SHELL_DIR := eic-shell
EIC_SHELL_INSTALL_SCRIPT := https://github.com/eic/eic-shell/raw/main/install.sh

.PHONY: all setup clean build-submodules setup-submodules

all: setup build-submodules

setup:
	@echo "Setting up eic-shell..."
	@mkdir -p $(EIC_SHELL_DIR)
	@cd $(EIC_SHELL_DIR) && curl -L $(EIC_SHELL_INSTALL_SCRIPT) | bash
	@echo "eic-shell setup complete."

setup-submodules:
	@echo "Initializing and updating submodules..."
	@git submodule update --init --recursive
	@echo "Submodules initialized and updated."

build-submodules: setup-submodules
	@echo "Building submodules..."
	@bash -c "cd submodules/epic-analysis && source environ.sh && make"
	@bash -c "cd submodules/tmd-eic-ana && make"
	@echo "Selected submodules built successfully."

clean:
	@echo "Cleaning up eic-shell directory..."
	@rm -rf $(EIC_SHELL_DIR)
	@echo "Cleanup complete."