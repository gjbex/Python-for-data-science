# Polars Exercises: Instructor Notes

This companion file provides brief model solutions and teaching notes for [`EXERCISES.md`](/home/gjb/Projects/Python-for-data-science/source-code/polars/EXERCISES.md). The sequence intentionally mirrors the pandas set so learners can compare the APIs directly.

## 1. Create a Series
Goal: basic `pl.Series` construction and summaries.  
Model: `s = pl.Series("values", [3, 5, 8, 13, 21])`; then `s.mean()`, `s.min()`, `s.max()`.  
Watch for: expecting label-based indexing like pandas.

## 2. Build a DataFrame
Goal: create a small frame and add one derived column.  
Model: `pl.DataFrame({...}).with_columns((pl.col("age") + 10).alias("age_in_10_years"))`.  
Watch for: trying to assign columns with pandas syntax.

## 3. Inspect Patient Metadata
Goal: load Excel data with Polars.  
Model: `df = pl.read_excel("data/patient_metadata.xlsx")`; inspect `.shape`, `.schema`, `.head()`.  
Watch for: wrong working directory or missing Excel support in another environment.

## 4. Filter Rows with Expressions
Goal: join data and filter with `pl.col(...)`.  
Model: join experiment and metadata on `patient`, then use `.filter(pl.col("temperature") > 38.5)`.  
Watch for: forgetting that Polars conditions are expressions, not plain boolean arrays.

## 5. Select Rows and Columns
Goal: basic row and column selection.  
Model: `df.select(["patient", "gender"]).head(4)` and `df.get_column("gender")`.  
Watch for: overusing pandas-style indexing syntax.

## 6. Missing-Value Count
Goal: identify null values.  
Model: build a small frame with `None` values and call `.null_count()`.  
Watch for: mixing `NaN` and `null` without discussing the distinction.

## 7. Fill or Drop Missing Values
Goal: compare `drop_nulls()` and `fill_null()`.  
Model: `df.drop_nulls()` and `df.with_columns(pl.col("score").fill_null(0))`.  
Watch for: filling string and numeric columns with the same default.

## 8. Clean Column Names
Goal: normalize headers.  
Model: build a rename mapping from old names to lowercase `snake_case`.  
Watch for: assuming Polars has the same `.str` accessor for column names as pandas.

## 9. Filter with Combined Conditions
Goal: combine predicates cleanly.  
Model: `.filter((pl.col("temperature") > 38.5) & (pl.col("gender") == "F"))`.  
Watch for: missing parentheses around each condition.

## 10. Sort and Rank
Goal: order rows and compute ranks.  
Model: `.sort("temperature", descending=True).with_columns(pl.col("temperature").rank("dense", descending=True).alias("temp_rank"))`.  
Watch for: rank syntax confusion; it is expression-based.

## 11. Group and Aggregate
Goal: grouped summaries.  
Model: `.group_by("condition").agg(pl.len().alias("count"), pl.col("temperature").mean(), pl.col("temperature").std())`.  
Watch for: using `count()` when learners really want the number of rows in each group.

## 12. Build a Pivot Table
Goal: cross-tab summary.  
Model: `.pivot(on="gender", index="condition", values="temperature", aggregate_function="mean")`.  
Watch for: omitting the aggregation and getting a duplicate-key error later.

## 13. Pivot with Duplicate Keys
Goal: explain how Polars handles ambiguous pivots.  
Model: use a tiny frame with duplicate `(patient, measure)` pairs; show that pivoting needs `aggregate_function`.  
Watch for: calling this “pivot vs pivot_table”; in Polars it is one pivot API with optional aggregation.

## 14. Long to Wide
Goal: reshape tidy data to wide format.  
Model: `df.pivot(on="day", index="patient", values="temperature")`.  
Watch for: duplicate key combinations.

## 15. Wide to Long
Goal: reshape repeated-measure columns into tidy form.  
Model: `df.unpivot(index="patient", variable_name="day", value_name="temperature")`.  
Watch for: forgetting to preserve the identifier column.

## 16. Classify with `when`/`then`
Goal: build conditional derived columns idiomatically.  
Model: chained `pl.when(...).then(...).otherwise(...)` inside `with_columns()`.  
Watch for: trying to write Python `if` logic over whole columns.

## 17. Reuse Expressions
Goal: keep transformations readable.  
Model: store the classification expression in a variable and reuse it in `with_columns()`.  
Watch for: duplicating the same threshold logic in multiple places.

## 18. Build a Method Chain
Goal: reinforce Polars’ pipeline style.  
Model: `experiment.join(...).filter(...).group_by(...).agg(...).sort(...)`.  
Watch for: falling back to many intermediate variables when one readable chain would do.

## 19. Read Generated CSV Data
Goal: connect the benchmark script to Polars I/O.  
Model: run `python create_csv_data.py sample --files 1 --cols 3 --rows 100`, then `pl.read_csv("sample_0001.csv", try_parse_dates=True)`.  
Watch for: reading the file from the wrong directory.

## 20. Mini Analysis
Goal: complete a small end-to-end workflow.  
Model: join the two Excel sheets, summarize mean temperature by condition and gender, and plot after converting with `.to_pandas()` if needed.  
Watch for: spending too much time on plotting instead of the data transformations.

## Teaching Tips
- Exercises 1 to 5 work well immediately after a pandas introduction because the API differences show up quickly.
- Exercises 11 to 18 make a strong comparison block against pandas groupby, pivot, and method chaining.
- Use the same patient datasets in both directories so learners can compare output, not just syntax.
