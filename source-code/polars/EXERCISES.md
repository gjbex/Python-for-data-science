# Polars Exercises

These short exercises are based on the notebooks and datasets in this directory. They are designed for 10 to 30 minutes each and intentionally parallel the `pandas` exercise set where that helps learners compare both libraries. Difficulty is marked as `Easy`, `Medium`, or `Medium+`.

## 1. Create a Series
Difficulty: `Easy`  
Time: 10 min  
Task: Create a `pl.Series` with five numbers. Compute the mean, minimum, and maximum.  
Expected solution: A Polars `Series` and simple summary methods or expressions.

## 2. Build a DataFrame
Difficulty: `Easy`  
Time: 10 min  
Task: Create a `pl.DataFrame` with columns `name`, `age`, and `city`. Add `age_in_10_years` with `with_columns()`.  
Expected solution: A small frame constructed from a dictionary and extended with one derived column.

## 3. Inspect Patient Metadata
Difficulty: `Easy`  
Time: 15 min  
Task: Load [`data/patient_metadata.xlsx`](/home/gjb/Projects/Python-for-data-science/source-code/polars/data/patient_metadata.xlsx), then show its shape, schema, and first rows.  
Expected solution: Correct use of `pl.read_excel()`, `.shape`, `.schema`, and `.head()`.

## 4. Filter Rows with Expressions
Difficulty: `Easy`  
Time: 15 min  
Task: Join the patient metadata and experiment data, then select rows with high temperature and rows for one condition.  
Expected solution: A joined frame and one or more `.filter()` expressions using `pl.col(...)`.

## 5. Select Rows and Columns
Difficulty: `Easy`  
Time: 10 min  
Task: Retrieve the first four rows of `patient` and `gender`, then retrieve only one column as a `Series`.  
Expected solution: Correct use of `.select()`, `.head()`, and single-column selection.

## 6. Missing-Value Count
Difficulty: `Easy`  
Time: 15 min  
Task: Create a small Polars `DataFrame` with missing values and count nulls per column.  
Expected solution: Use of `.null_count()` and interpretation of the result.

## 7. Fill or Drop Missing Values
Difficulty: `Medium`  
Time: 15 min  
Task: On the same small frame, create one cleaned version with `drop_nulls()` and one with `fill_null()`.  
Expected solution: Two cleanup strategies and a short explanation of when each is appropriate.

## 8. Clean Column Names
Difficulty: `Easy`  
Time: 10 min  
Task: Rename deliberately messy headers to lowercase `snake_case`.  
Expected solution: Use of `.rename()` or a small mapping generated from the existing column names.

## 9. Filter with Combined Conditions
Difficulty: `Medium`  
Time: 15 min  
Task: Reproduce one filter with two conditions in a single `.filter()` call.  
Expected solution: A concise Polars expression using `&` or multiple predicates.

## 10. Sort and Rank
Difficulty: `Easy`  
Time: 10 min  
Task: Sort experiment rows by temperature and add a dense rank column.  
Expected solution: Use of `.sort()` and an expression-based rank in `with_columns()`.

## 11. Group and Aggregate
Difficulty: `Medium`  
Time: 20 min  
Task: Group the merged patient data by one category and compute count, mean, and standard deviation of temperature.  
Expected solution: A `group_by(...).agg(...)` summary.

## 12. Build a Pivot Table
Difficulty: `Medium`  
Time: 20 min  
Task: Create a pivot table with condition on rows, gender on columns, and mean temperature as the aggregate.  
Expected solution: A Polars `pivot()` call with an explicit aggregation.

## 13. Pivot with Duplicate Keys
Difficulty: `Medium`  
Time: 15 min  
Task: Build a small table with duplicate `(patient, measure)` pairs and show why a pivot needs an aggregation.  
Expected solution: A small example where plain pivoting is ambiguous and `aggregate_function="mean"` resolves it.

## 14. Long to Wide
Difficulty: `Medium`  
Time: 20 min  
Task: Create a tidy long-format table and reshape it to wide form with `pivot()`.  
Expected solution: Correct choice of `index`, `on`, and `values`.

## 15. Wide to Long
Difficulty: `Medium`  
Time: 20 min  
Task: Convert a table with columns like `day1`, `day2`, and `day3` into long format with `unpivot()` or `melt()`.  
Expected solution: A tidy long-format table with clear variable and value columns.

## 16. Classify with `when`/`then`
Difficulty: `Medium`  
Time: 15 min  
Task: Map temperatures to categories such as `normal`, `elevated`, and `high`.  
Expected solution: A new column built with `pl.when(...).then(...).otherwise(...)`.

## 17. Reuse Expressions
Difficulty: `Medium+`  
Time: 15 min  
Task: Refactor the temperature classification so the expression is defined once and reused in `with_columns()`.  
Expected solution: A named Polars expression or a small helper that keeps the pipeline readable.

## 18. Build a Method Chain
Difficulty: `Medium+`  
Time: 20 min  
Task: Chain together a join, filter, group-by, and sort into one readable workflow.  
Expected solution: A compact Polars pipeline with no intermediate mutation required.

## 19. Read Generated CSV Data
Difficulty: `Medium`  
Time: 20 min  
Task: Use [`create_csv_data.py`](/home/gjb/Projects/Python-for-data-science/source-code/polars/create_csv_data.py) to generate a CSV file, then load it with Polars and inspect the schema.  
Expected solution: Correct use of the generator script and `pl.read_csv()`.

## 20. Mini Analysis
Difficulty: `Medium+`  
Time: 30 min  
Task: Merge the patient spreadsheets, summarize mean temperature by condition and gender, and produce one simple plot after converting to pandas if needed.  
Expected solution: A small end-to-end workflow with join, cleanup, summary, and a quick visualization.

## Suggested Verification
- Re-run notebook cells from a clean kernel.
- Check row counts before and after joins and filters.
- For `group_by()` and `pivot()`, verify that grouped totals agree with the source data.
- For reshaping exercises, check that the expected number of values is preserved.
