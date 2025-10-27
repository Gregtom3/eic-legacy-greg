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

### Building the Project
This repository includes a `Makefile` to simplify the setup and build process. To set up the environment and build all submodules, run:

```bash
make all
```

The `make all` command will:
1. Set up the `eic-shell` environment.
2. Build the `tmd-eic-ana` submodule.
3. Build the remaining submodules (`tmd-eic-ana` and `epic-analysis`) within the `eic-shell`.
4. Build the `epic-analysis` submodule within the `eic-shell` environment.

**Note:** If the `eic-shell` script cannot be downloaded automatically, you can manually download it from the [eic-shell repository](https://github.com/eic/eic-shell) and place it in the `eic-shell` directory.

To clean up the `eic-shell` directory, you can run:

```bash
make clean
```
