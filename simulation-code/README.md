# Code to Replicate Simulation Experiments

# Installation

Install [conda](https://docs.anaconda.com/miniconda/) for your system, as well as [poetry](https://python-poetry.org/docs/). Then type:

```commandline
conda create -n simulation python=3.8
conda activate simulation
poetry install
```

# Run Experiments

Without delay:

```commandline
python test_gen_palyndrome.py --max-string-length 100 --runs-rand 100 --runs-dist 100 --runs-bigrams 100
```

With delay:

```commandline
python test_gen_palyndrome.py --max-string-length 100 --runs-rand 100 --runs-dist 100 --runs-bigrams 100 --delay
```

Please refer to the paper for an estimation of how much time the experiments take.
