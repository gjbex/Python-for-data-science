# Set up the training environment with Pixi

This repository uses [Pixi](https://pixi.prefix.dev/latest/) to install Python,
JupyterLab, and the libraries used by the training material. The commands below
are for a Linux terminal.

## Install Pixi

The installer recommended by the Pixi project is:

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

This command downloads and immediately executes the installer. If you prefer to
inspect a remote script before running it, use:

```bash
curl -fsSL https://pixi.sh/install.sh -o /tmp/pixi-install.sh
less /tmp/pixi-install.sh
sh /tmp/pixi-install.sh
```

The installer puts `pixi` in `~/.pixi/bin` and updates the shell startup file so
that the command is on `PATH`. Start a new terminal, then verify the installation:

```bash
pixi --version
```

See the [official Pixi installation instructions](https://pixi.prefix.dev/latest/installation/)
for installer options and alternative installation methods.

## Create an environment

Run Pixi commands from the top-level directory of this repository, where
`pixi.toml` is located:

```bash
cd /path/to/Python-for-data-science
```

To create the default environment containing the complete current training
stack, run:

```bash
pixi install
```

The initial solve and download can take some time, particularly because the
default environment includes the geospatial libraries. Later invocations reuse
the environment. The first install also creates or updates `pixi.lock`, which
records the resolved package versions.

### Create a smaller topic environment

If you only need one part of the training, install its environment explicitly.
For example:

```bash
pixi install --environment pandas
pixi install --environment gis
```

The available topic environments are:

- `altair`
- `db-access`
- `duckdb`
- `gis`
- `holoviews`
- `networkx`
- `oscillator`
- `pandas`
- `polars`
- `regexes`
- `seaborn`
- `web-scraping`
- `xarray`

There is also a separate `pandas-bokeh` environment for the historical notebook
under `source-code/pandas/bokeh`. It deliberately uses an older Python, NumPy,
Pandas, and Bokeh stack and should not be used for the other notebooks.

You can create every environment with `pixi install --all`, but this duplicates
many packages across separate environments and consumes substantially more disk
space. Usually the default environment or one topic environment is sufficient.

## Run a notebook

Start JupyterLab with the complete default environment:

```bash
pixi run lab
```

JupyterLab opens in `source-code`. Select a topic directory and open the desired
`.ipynb` file. Run notebook cells with **Shift+Enter**.

To use a topic-specific environment, select it with `--environment` (or `-e`):

```bash
pixi run --environment pandas lab
pixi run -e gis lab
```

For the isolated legacy Bokeh example, run:

```bash
pixi run --environment pandas-bokeh lab
```

Stop JupyterLab by returning to the terminal and pressing **Ctrl+C**. Pixi does
not require manual environment activation for these commands; `pixi run` runs
the task inside the selected environment and creates that environment first if
it has not yet been installed.
