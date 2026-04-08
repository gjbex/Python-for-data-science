# Pandas Exercises

These short exercises are based on the notebooks and datasets in this directory. They are designed for 10 to 30 minutes each and can be solved in a notebook or in a Python REPL. Difficulty is marked as `Easy`, `Medium`, or `Medium+`.

## 1. Create a Series
Difficulty: `Easy`  
Time: 10 min  
Task: Create a `Series` with five numbers and custom labels. Compute `mean()`, `min()`, and `max()`.  
Expected solution: A labeled `Series`; correct use of label-based access and simple summary methods.

## 2. Build a DataFrame
Difficulty: `Easy`  
Time: 10 min  
Task: Create a `DataFrame` with columns `name`, `age`, and `city`. Add `age_in_10_years`.  
Expected solution: A small `DataFrame` built from a dictionary and a derived numeric column.

## 3. Inspect Patient Metadata
Difficulty: `Easy`  
Time: 15 min  
Task: Load [`data/patient_metadata.xlsx`](/home/gjb/Projects/Python-for-data-science/source-code/pandas/data/patient_metadata.xlsx), then show shape, dtypes, and first rows.  
Expected solution: Correct use of `pd.read_excel()`, `.shape`, `.dtypes`, and `.head()`.

## 4. Filter Rows with Boolean Masks
Difficulty: `Easy`  
Time: 15 min  
Task: Select patients above an age threshold and rows matching one categorical value.  
Expected solution: Two filtered `DataFrame` objects using boolean masks with `&`, `|`, and parentheses where needed.

## 5. Compare `.loc` and `.iloc`
Difficulty: `Easy`  
Time: 10 min  
Task: Retrieve the same subset once with `.loc` and once with `.iloc`.  
Expected solution: Clear distinction between label-based and position-based indexing.

## 6. Missing-Value Count
Difficulty: `Easy`  
Time: 15 min  
Task: Load [`data/missing_values.csv`](/home/gjb/Projects/Python-for-data-science/source-code/pandas/data/missing_values.csv) and count missing values per column.  
Expected solution: Correct use of `.isna().sum()` and optional sorting of the result.

## 7. Fill or Drop Missing Values
Difficulty: `Medium`  
Time: 15 min  
Task: Produce one cleaned table with `dropna()` and one with `fillna()`.  
Expected solution: Two different cleanup strategies and a short explanation of when each is appropriate.

## 8. Clean Column Names
Difficulty: `Easy`  
Time: 10 min  
Task: Convert column names to lowercase `snake_case`.  
Expected solution: Use of `df.columns` with string methods such as `.str.lower()` and `.str.replace()`.

## 9. Query Syntax Practice
Difficulty: `Medium`  
Time: 15 min  
Task: Reproduce one boolean-mask filter using `.query()`.  
Expected solution: Equivalent filter written with a query string and matching row counts.

## 10. Sort and Rank
Difficulty: `Easy`  
Time: 10 min  
Task: Sort by one numeric column and add a dense rank.  
Expected solution: Use of `.sort_values()` and `.rank(method="dense")`.

## 11. Group and Aggregate
Difficulty: `Medium`  
Time: 20 min  
Task: Group patient metadata by one category and compute count, mean, and standard deviation.  
Expected solution: A grouped summary using `.groupby()` and `.agg()`.

## 12. Build a Pivot Table
Difficulty: `Medium`  
Time: 20 min  
Task: Create a pivot table with one categorical variable on rows and another on columns.  
Expected solution: Use of `pd.pivot_table()` with an explicit aggregation function.

## 13. `pivot()` vs `pivot_table()`
Difficulty: `Medium`  
Time: 15 min  
Task: Construct duplicate key combinations and show why `pivot()` fails while `pivot_table()` succeeds.  
Expected solution: A small example demonstrating uniqueness requirements and aggregation.

## 14. Long to Wide
Difficulty: `Medium`  
Time: 20 min  
Task: Create a tidy long-format table and reshape it to wide form.  
Expected solution: Correct use of `pivot()` with sensible index, column, and value fields.

## 15. Wide to Long
Difficulty: `Medium`  
Time: 20 min  
Task: Convert a table with columns like `day1`, `day2`, and `day3` into long format.  
Expected solution: Use of `melt()` and clear variable/value column names.

## 16. Classify with `apply()`
Difficulty: `Medium`  
Time: 15 min  
Task: Write a function that maps a numeric value to `low`, `medium`, or `high`, then apply it row-wise or column-wise.  
Expected solution: A custom function and a new classification column created with `apply()`.

## 17. Replace `apply()` with Vectorization
Difficulty: `Medium+`  
Time: 15 min  
Task: Solve the same classification problem without `apply()`.  
Expected solution: Use of boolean masks or `np.select()` and a short comparison of both approaches.

## 18. Build a `.pipe()` Workflow
Difficulty: `Medium+`  
Time: 20 min  
Task: Chain together renaming, filtering, and summarizing steps using `.pipe()`.  
Expected solution: A readable, multi-step pipeline with small helper functions.

## 19. Read Non-Standard CSV Files
Difficulty: `Medium`  
Time: 20 min  
Task: Use [`generate_csv_files.py`](/home/gjb/Projects/Python-for-data-science/source-code/pandas/generate_csv_files.py) to create CSV files with unusual separators or line endings, then load them with pandas.  
Expected solution: Correct use of script options and matching `pd.read_csv()` parameters such as `sep=`.

## 20. Mini Analysis
Difficulty: `Medium+`  
Time: 30 min  
Task: Choose one file from [`data/`](/home/gjb/Projects/Python-for-data-science/source-code/pandas/data), clean it, summarize it, and produce one plot.  
Expected solution: A compact end-to-end workflow with import, cleanup, summary statistics, and a plot that matches the cleaned data.

## Suggested Verification
- Re-run notebook cells from a clean kernel.
- Check shapes before and after filtering or reshaping.
- Compare row counts when translating between boolean masks and `.query()`.
- For pivots and groupbys, verify that totals match the source data.
