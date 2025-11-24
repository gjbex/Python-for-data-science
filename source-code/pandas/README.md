# Pandas
pandas is a library that defines three data structures and algorithms
that are useful in the context of data analysis and data science.  It
represents `Series`, `DataFrame`, and `Panel`, or 1D, 2D, and 3D arrays.
`DataFrame` is especially useful, and defines methods such as `pivot_table`,
and `query`, and has many facilities to deal with missing data.

For analysis purposes, pandas has some nice plotting features that are
easy to use.

## What is it?
1. `agt_analysis.ipynb`: a notebook illustrating the analysis and
    visualization of water levels as measured by variouus sensors.
1. `agt_data`: three CSV files using in the notebook.
1. `data_generation.ipynb`: notebook that generates some simulated gene
    expression data using `numpy` and 'pandas`.
1. `pandas_intro.ipynb`: illustrates various aspects of using pandas such
    as importing data, using `Series`, `DataFrame`, cleaning and formatting
    data, dealing with missing data, adding and removing columns, and
    various algorithms and visualizations.
1. `data`: some data sets used in the notebook above.
1. `patients.ipynb`: runninng example used in the Python slides.
1. `patient_data.ipynb`: extended version of therunninng example used
    in the Python slides.
1. `pipes.ipynb`: consolidating data processing using pipes.
1. `screenshots`: screenshots made for the slides.
1. `generate_csv_files.py`: script to generate CSV files in different
    formatg.
1. `copy_on_write.ipynb`: Jupyter notebook that illustrates how data is shared
   between related notebooks and the role Copy-on-Write plays in order to
   prevent accidental data modifications in more than one dataframe.
1. `apply.ipynb`: Jupyter notebook that illustrates the use of the `apply` method
   in pandas dataframes for applying functions along rows or columns. It includes
   a comparison of performance between using `apply` and vectorized operations.
1. `numba_and_pandas.ipynb`: Jupyter notebook that demonstrates how to use Numba
   to optimize performance of operations on pandas dataframes.
