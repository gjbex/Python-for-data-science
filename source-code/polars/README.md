# Polars

Polars is an alternative to pandas that is designed to have better performance.


## What is it?

1. `patient_data.ipynb`: Jupyter notebook that explores functional differences
   between pandas and polars.  It replicates the notebook in the `pandas`
   directory with the same name.
1. `polars_large_data_benchmark.ipynb`: Jupyter notebook that compares the
   performance of polars and pandas on large data sets.
1. `create_csv_data.py`: Python script to generate one or more large CSV files
   for benchmarking.
1. `create_csv_data.slurm`: Slurm script to run `create_csv_data.py` on a
   cluster.
1. `polars_performance.ipynb`: Jupyter notebook that compares the performance
   of polars and pandas on a variety of operations.
1. `data`: Directory containing the data used in the notebook.
