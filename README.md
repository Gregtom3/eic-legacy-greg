# eic-legacy-greg
Legacy code for existing EIC projects (hopefully) organized enough for reproducibility.

## Submodules
This repository includes the following submodules:

- [tmd-eic-ana](https://github.com/Gregtom3/tmd-eic-ana): Analysis tools for TMD studies in EIC.
- [epic-analysis](https://github.com/eic/epic-analysis/tree/dihadron): Analysis tools for dihadron studies in EIC. This project loads the `dihadron` branch which has some unmerged features.

### Cloning the Repository
To clone this repository along with its submodules, use the following command:

```bash
git clone --recurse-submodules https://github.com/Gregtom3/eic-legacy-greg.git
```

If you have already cloned the repository and want to initialize the submodules, run:

```bash
git submodule update --init --recursive
```

To update all submodules to their latest remote changes, run:

```bash
make update
```

### Building the Project
This repository includes a `Makefile` to simplify the setup and build process. If you do not already have it setup, you can install the latest version of `eic-shell` with:

```bash
make eic-shell
```

You can then enter into the `eic-shell` with the following command:

```bash
./eic-shell/eic-shell
```

To set up the environment and build all submodules, you must first be inside the `eic-shell`. The `epic-analysis` submodule requires `delphes`. A first time installation can be run:

```bash
make delphes
```

Then, to install the remaining submodules, run:

```bash
make all
```

**Note:** If the `eic-shell` script cannot be downloaded automatically, you can manually download it from the [eic-shell repository](https://github.com/eic/eic-shell) and place it in the `eic-shell` directory.

To clean up the `eic-shell` directory, you can run:

```bash
make clean-eic-shell
```

To clean up the submodules, you can run:

```bash
make clean
```

### Setting Up a Virtual Environment

To set up a Python virtual environment for this project, follow these steps:

1. **Create the Virtual Environment**:
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the Virtual Environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Deactivate the Virtual Environment** (when done):
   ```bash
   deactivate
   ```
