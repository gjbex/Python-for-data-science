# Pandas Exercises: Instructor Notes

This companion file provides brief model solutions and teaching notes for [`EXERCISES.md`](/home/gjb/Projects/Python-for-data-science/source-code/pandas/EXERCISES.md). The examples are intentionally compact so you can adapt them live in a notebook.

## 1. Create a Series
Goal: basic `Series` construction and indexing.  
Model: `s = pd.Series([3, 5, 8, 13, 21], index=["a", "b", "c", "d", "e"])` then `s.mean()`, `s.min()`, `s.max()`, `s["b"]`, `s.iloc[2]`.  
Watch for: confusion between label access and positional access.

## 2. Build a DataFrame
Goal: create columns and derive one new column.  
Model: `df = pd.DataFrame({"name": [...], "age": [...], "city": [...]})`; `df["age_in_10_years"] = df["age"] + 10`.  
Watch for: mixing row-oriented and column-oriented constructors.

## 3. Inspect Patient Metadata
Goal: load Excel and inspect structure.  
Model: `df = pd.read_excel("data/patient_metadata.xlsx")`; use `.shape`, `.dtypes`, `.head()`.  
Watch for: wrong working directory.

## 4. Filter Rows with Boolean Masks
Goal: build compound conditions.  
Model: `df[df["age"] > 50]`; `df[(df["age"] > 50) & (df["sex"] == "F")]`.  
Watch for: missing parentheses around conditions.

## 5. Compare `.loc` and `.iloc`
Goal: distinguish labels from positions.  
Model: `df.loc[0:4, ["age"]]` versus `df.iloc[0:5, [2]]` or equivalent.  
Watch for: assuming `.loc` end indices are exclusive.

## 6. Missing-Value Count
Goal: identify incomplete columns.  
Model: `df.isna().sum().sort_values(ascending=False)`.  
Watch for: using `.count()`, which counts non-missing values.

## 7. Fill or Drop Missing Values
Goal: compare cleanup strategies.  
Model: `df_drop = df.dropna()` and `df_fill = df.fillna({"col1": 0, "col2": "unknown"})`.  
Watch for: applying one fill value to incompatible column types.

## 8. Clean Column Names
Goal: normalize headers.  
Model: `df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False))`.  
Watch for: accidental regex behavior in `str.replace()`.

## 9. Query Syntax Practice
Goal: translate masks to `.query()`.  
Model: `df.query("age > 50 and sex == 'F'")`.  
Watch for: forgetting quotes around strings.

## 10. Sort and Rank
Goal: order rows and compute ranks.  
Model: `df = df.sort_values("age", ascending=False)`; `df["rank"] = df["age"].rank(method="dense", ascending=False)`.  
Watch for: rank values becoming floats by default.

## 11. Group and Aggregate
Goal: grouped summaries.  
Model: `df.groupby("sex")["age"].agg(["count", "mean", "std"])` or a multi-column `.agg({...})`.  
Watch for: grouping on high-cardinality columns that produce noisy output.

## 12. Build a Pivot Table
Goal: introduce cross-tab summaries.  
Model: `pd.pivot_table(df, index="sex", columns="smoker", values="age", aggfunc="mean")`.  
Watch for: choosing non-numeric values with a numeric aggregation.

## 13. `pivot()` vs `pivot_table()`
Goal: show uniqueness constraints.  
Model: create duplicate `(id, variable)` rows; `pivot()` raises, `pivot_table(..., aggfunc="mean")` works.  
Watch for: examples without duplicates, which hide the distinction.

## 14. Long to Wide
Goal: reshape tidy data.  
Model: `long_df.pivot(index="patient", columns="day", values="value")`.  
Watch for: duplicate index/column combinations.

## 15. Wide to Long
Goal: reshape repeated-measure columns.  
Model: `df.melt(id_vars=["patient"], var_name="day", value_name="value")`.  
Watch for: forgetting to preserve identifier columns.

## 16. Classify with `apply()`
Goal: use a custom function.  
Model:
```python
def classify(x):
    if x < 10:
        return "low"
    if x < 20:
        return "medium"
    return "high"

df["risk"] = df["score"].apply(classify)
```
Watch for: using row-wise `axis=1` when a single-column operation is enough.

## 17. Replace `apply()` with Vectorization
Goal: contrast vectorized logic with `apply()`.  
Model: `np.select([df["score"] < 10, df["score"] < 20], ["low", "medium"], default="high")`.  
Watch for: condition order; earlier conditions win.

## 18. Build a `.pipe()` Workflow
Goal: make multi-step transformations readable.  
Model:
```python
def clean_names(df):
    df = df.copy()
    df.columns = df.columns.str.lower()
    return df

summary = (
    df.pipe(clean_names)
      .query("age > 50")
      .groupby("sex")["age"]
      .mean()
)
```
Watch for: helper functions that mutate in place unexpectedly.

## 19. Read Non-Standard CSV Files
Goal: connect file generation to import options.  
Model: run `python generate_csv_files.py --columns int float string --separator ';' --file-type Windows`; read with `pd.read_csv(..., sep=';')`.  
Watch for: mismatched separators or newline assumptions.

## 20. Mini Analysis
Goal: complete a small end-to-end workflow.  
Model: load one file, normalize columns, handle nulls, group or summarize, then plot with `df.plot()` or `plt`.  
Watch for: spending too long on plotting aesthetics instead of data handling.

## Teaching Tips
- Prefer the patient spreadsheets and `missing_values.csv` for short exercises; they are concrete and require little setup.
- Exercises 11 to 18 combine well into a 60 to 90 minute workshop block.
- If learners are new to pandas, keep `apply()`, `pivot_table()`, and `.pipe()` separate rather than chaining them in one task.
