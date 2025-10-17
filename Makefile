# Makefile for setting up the eic-shell and building submodules

EIC_SHELL_DIR := eic-shell
EIC_SHELL_INSTALL_SCRIPT := https://github.com/eic/eic-shell/raw/main/install.sh

.PHONY: all setup clean build-submodules

all: setup build-submodules

setup:
	@echo "Setting up eic-shell..."
	@mkdir -p $(EIC_SHELL_DIR)
	@cd $(EIC_SHELL_DIR) && curl -L $(EIC_SHELL_INSTALL_SCRIPT) | bash
	@echo "eic-shell setup complete."

build-submodules:
	@echo "Building submodules..."
	@cd submodules/eicQuickSim && \
		python3 -m venv --clear --without-pip --copies .eicQuickSim && \
		. .eicQuickSim/bin/activate && \
		pip install --upgrade pip setuptools wheel && \
		pip install -r requirements.txt && \
		make install
	@cd submodules/epic-analysis && \
		. environ.sh && \
		make
	@cd submodules/tmd-eic-ana && make
	@echo "All submodules built successfully."

clean:
	@echo "Cleaning up eic-shell directory..."
	@rm -rf $(EIC_SHELL_DIR)
	@echo "Cleanup complete."