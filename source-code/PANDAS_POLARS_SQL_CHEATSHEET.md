# Pandas, Polars, and DuckDB SQL Cheat Sheet

This cheat sheet maps common analysis concepts from the patient-analysis notebooks to idiomatic patterns in pandas, Polars, and DuckDB SQL. The goal is best practice in each tool, not line-by-line syntax equivalence. The examples assume two tables with the same structure as the notebooks:

- `patient_experiment(patient, date, temperature, dose)`
- `patient_metadata(patient, gender, condition)`

## Filter One Patient

Get all measurements for patient `6`. Concept: row filtering by exact match.

### pandas
```python
experiment[experiment["patient"] == 6]
```

### polars
```python
experiment.filter(pl.col("patient") == 6)
```

### DuckDB SQL
```sql
SELECT patient, date, temperature, dose
FROM patient_experiment
WHERE patient = 6;
```

## Filter with Multiple Conditions

Keep rows where temperature is above `38.5` and dose is positive. Concept: boolean filtering with combined predicates.

### pandas
```python
experiment[
    (experiment["temperature"] > 38.5)
    & (experiment["dose"] > 0)
]
```

### polars
```python
experiment.filter(
    (pl.col("temperature") > 38.5)
    & (pl.col("dose") > 0)
)
```

### DuckDB SQL
```sql
SELECT patient, date, temperature, dose
FROM patient_experiment
WHERE temperature > 38.5
  AND dose > 0;
```

## Sort Rows

Sort all measurements by temperature, highest first. Concept: ordering rows by one key.

### pandas
```python
experiment.sort_values("temperature", ascending=False)
```

### polars
```python
experiment.sort("temperature", descending=True)
```

### DuckDB SQL
```sql
SELECT patient, date, temperature, dose
FROM patient_experiment
ORDER BY temperature DESC;
```

## Create a Derived Category

Map each temperature to `normal`, `elevated`, or `high`. Concept: deriving categorical variables from continuous values.

### pandas
```python
classified = experiment.copy()
classified["band"] = pd.cut(
    classified["temperature"],
    bins=[-float("inf"), 38.0, 38.5, float("inf")],
    labels=["normal", "elevated", "high"],
    right=False,
)
```

`pd.cut` is usually the clearest pandas choice when you are binning continuous numeric values into named intervals.

### polars
```python
classified = experiment.with_columns(
    pl.when(pl.col("temperature") < 38.0)
    .then(pl.lit("normal"))
    .when(pl.col("temperature") < 38.5)
    .then(pl.lit("elevated"))
    .otherwise(pl.lit("high"))
    .alias("band")
)
```

Polars does not have a direct equivalent that is as central as `pd.cut`, so explicit expressions are usually the most readable option.

### DuckDB SQL
```sql
SELECT
    patient,
    date,
    temperature,
    dose,
    CASE
        WHEN temperature < 38.0 THEN 'normal'
        WHEN temperature < 38.5 THEN 'elevated'
        ELSE 'high'
    END AS band
FROM patient_experiment;
```

## Aggregate Per Patient

Compute the maximum temperature and total dose for each patient. Concept: group-by aggregation over entities.

### pandas
```python
experiment.groupby("patient").agg(
    max_temperature=("temperature", "max"),
    total_dose=("dose", "sum"),
).reset_index()
```

### polars
```python
experiment.group_by("patient").agg(
    pl.col("temperature").max().alias("max_temperature"),
    pl.col("dose").sum().alias("total_dose"),
).sort("patient")
```

### DuckDB SQL
```sql
SELECT
    patient,
    MAX(temperature) AS max_temperature,
    SUM(dose) AS total_dose
FROM patient_experiment
GROUP BY patient;
```

In pandas and Polars it is often clearer to materialize grouped results as a regular table rather than leave the grouping key only in the index.

## Aggregate with a Filter

Count high-fever measurements per patient, only for temperatures above `39.5`. Concept: filter first, then aggregate.

### pandas
```python
experiment[experiment["temperature"] > 39.5] \
    .groupby("patient") \
    .agg(
        high_fever_count=("temperature", "size"),
        max_temperature=("temperature", "max"),
    ) \
    .reset_index()
```

### polars
```python
experiment.filter(pl.col("temperature") > 39.5) \
    .group_by("patient") \
    .agg(
        pl.len().alias("high_fever_count"),
        pl.col("temperature").max().alias("max_temperature"),
    ) \
    .sort("patient")
```

### DuckDB SQL
```sql
SELECT
    patient,
    COUNT(*) AS high_fever_count,
    MAX(temperature) AS max_temperature
FROM patient_experiment
WHERE temperature > 39.5
GROUP BY patient
ORDER BY patient;
```

## Filter Aggregated Results

Keep only patients whose maximum temperature exceeds `39`. Concept: post-aggregation filtering.

### pandas
```python
summary = experiment.groupby("patient").agg(
    max_temperature=("temperature", "max")
).reset_index()
summary[summary["max_temperature"] > 39]
```

### polars
```python
experiment.group_by("patient").agg(
    pl.col("temperature").max().alias("max_temperature")
).filter(
    pl.col("max_temperature") > 39
)
```

### DuckDB SQL
```sql
SELECT
    patient,
    MAX(temperature) AS max_temperature
FROM patient_experiment
GROUP BY patient
HAVING MAX(temperature) > 39;
```

## Join Experiment Data with Metadata

Combine temperature measurements with gender and condition. Concept: joining fact data with descriptive metadata.

### pandas
```python
patients = experiment.merge(metadata, on="patient", how="inner")
```

### polars
```python
patients = experiment.join(metadata, on="patient", how="inner")
```

### DuckDB SQL
```sql
SELECT *
FROM patient_experiment AS exp
INNER JOIN patient_metadata AS mt
USING (patient);
```

## Find IDs Present in Only One Table

Identify patients that appear in the experiment table or metadata table, but not both. Concept: key reconciliation and data-quality checks across tables.

### pandas
```python
outer = experiment.merge(metadata, on="patient", how="outer", indicator=True)
outer[outer["_merge"] != "both"]
```

### polars
```python
experiment.join(metadata, on="patient", how="full")
```

Then inspect the nulls in the joined columns to determine which side is missing.

### DuckDB SQL
```sql
SELECT
    COALESCE(exp.patient, mt.patient) AS patient,
    CASE
        WHEN exp.patient IS NOT NULL AND mt.patient IS NULL
            THEN 'only in experiment'
        WHEN exp.patient IS NULL AND mt.patient IS NOT NULL
            THEN 'only in metadata'
        ELSE 'in both'
    END AS present
FROM patient_experiment AS exp
FULL OUTER JOIN patient_metadata AS mt
USING (patient)
WHERE exp.patient IS NULL
   OR mt.patient IS NULL;
```

## Summarize by Category After a Join

Compute mean temperature by condition. Concept: join first, then aggregate by category.

### pandas
```python
patients = experiment.merge(metadata, on="patient")
patients.groupby("condition", as_index=False)["temperature"].mean()
```

### polars
```python
patients = experiment.join(metadata, on="patient", how="inner")
patients.group_by("condition").agg(
    pl.col("temperature").mean().alias("mean_temperature")
).sort("condition")
```

### DuckDB SQL
```sql
SELECT
    mt.condition,
    AVG(exp.temperature) AS mean_temperature
FROM patient_experiment AS exp
INNER JOIN patient_metadata AS mt
USING (patient)
GROUP BY mt.condition
ORDER BY mt.condition;
```

## Pivot by Condition and Gender

Compare mean temperature by condition and gender. Concept: reshaping grouped summaries into a cross-tab.

### pandas
```python
patients = experiment.merge(metadata, on="patient")
patients.pivot_table(
    index="condition",
    columns="gender",
    values="temperature",
    aggfunc="mean",
    observed=False,
)
```

`pivot_table` is the idiomatic pandas choice because it handles aggregation directly.

### polars
```python
patients = experiment.join(metadata, on="patient", how="inner")
patients.pivot(
    on="gender",
    index="condition",
    values="temperature",
    aggregate_function="mean",
)
```

In Polars, `pivot` with an explicit aggregation is the closest high-level reshaping tool.

### DuckDB SQL
```sql
PIVOT (
    SELECT
        mt.condition,
        mt.gender,
        exp.temperature
    FROM patient_experiment AS exp
    INNER JOIN patient_metadata AS mt
    USING (patient)
)
ON gender
USING AVG(temperature)
GROUP BY condition;
```

### DuckDB SQL Without `PIVOT`
```sql
SELECT
    mt.condition,
    AVG(CASE WHEN mt.gender = 'F' THEN exp.temperature END) AS F,
    AVG(CASE WHEN mt.gender = 'M' THEN exp.temperature END) AS M
FROM patient_experiment AS exp
INNER JOIN patient_metadata AS mt
USING (patient)
GROUP BY mt.condition
ORDER BY mt.condition;
```

## Reuse an Intermediate Result

Save a derived summary and query it again later. Concept: materializing intermediate results for reuse.

### pandas
```python
hypothesis = experiment.groupby("patient").agg(
    max_temperature=("temperature", "max"),
    total_dose=("dose", "sum"),
).reset_index()

hypothesis["total_dose"].max()
```

### polars
```python
hypothesis = experiment.group_by("patient").agg(
    pl.col("temperature").max().alias("max_temperature"),
    pl.col("dose").sum().alias("total_dose"),
)

hypothesis.select(pl.col("total_dose").max())
```

### DuckDB SQL
```sql
CREATE VIEW hypothesis AS
SELECT
    patient,
    MAX(temperature) AS max_temperature,
    SUM(dose) AS total_dose
FROM patient_experiment
GROUP BY patient;
```

Then:

```sql
SELECT MAX(total_dose)
FROM hypothesis;
```

## Time-Based Summary

Compute mean temperature per day. Concept: time bucketing and temporal aggregation.

### pandas
```python
daily = experiment.copy()
daily["day"] = daily["date"].dt.floor("D")
daily.groupby("day", as_index=False)["temperature"].mean()
```

### polars
```python
experiment.with_columns(
    pl.col("date").dt.truncate("1d").alias("day")
).group_by("day").agg(
    pl.col("temperature").mean().alias("mean_temperature")
).sort("day")
```

### DuckDB SQL
```sql
SELECT
    DATE_TRUNC('day', date) AS day,
    AVG(temperature) AS mean_temperature
FROM patient_experiment
GROUP BY day
ORDER BY day;
```

## Previous Value Per Patient

Compare each temperature to the previous measurement for the same patient. Concept: within-group window calculations over ordered data.

### pandas
```python
ordered = experiment.sort_values(["patient", "date"]).copy()
ordered["prev_temperature"] = ordered.groupby("patient")["temperature"].shift(1)
```

For ordered comparisons within groups, `groupby(...).shift()` is the standard pandas pattern.

### polars
```python
experiment.sort(["patient", "date"]).with_columns(
    pl.col("temperature").shift(1).over("patient").alias("prev_temperature")
)
```

### DuckDB SQL
```sql
SELECT
    patient,
    date,
    temperature,
    LAG(temperature) OVER (
        PARTITION BY patient
        ORDER BY date
    ) AS prev_temperature
FROM patient_experiment;
```

## Running Total Dose

Compute cumulative dose per patient over time. Concept: cumulative window aggregation.

### pandas
```python
ordered = experiment.sort_values(["patient", "date"]).copy()
ordered["cumulative_dose"] = ordered.groupby("patient")["dose"].cumsum()
```

`groupby(...).cumsum()` is the usual pandas idiom for running totals.

### polars
```python
experiment.sort(["patient", "date"]).with_columns(
    pl.col("dose").cum_sum().over("patient").alias("cumulative_dose")
)
```

### DuckDB SQL
```sql
SELECT
    patient,
    date,
    dose,
    SUM(dose) OVER (
        PARTITION BY patient
        ORDER BY date
    ) AS cumulative_dose
FROM patient_experiment;
```

## Ranking Patients

Rank patients by maximum temperature. Concept: ranking grouped results.

### pandas
```python
summary = experiment.groupby("patient").agg(
    max_temperature=("temperature", "max")
).reset_index()
summary["temp_rank"] = summary["max_temperature"].rank(
    method="dense",
    ascending=False,
)
```

### polars
```python
experiment.group_by("patient").agg(
    pl.col("temperature").max().alias("max_temperature")
).with_columns(
    pl.col("max_temperature").rank(
        method="dense",
        descending=True,
    ).alias("temp_rank")
)
```

### DuckDB SQL
```sql
SELECT
    patient,
    MAX(temperature) AS max_temperature,
    RANK() OVER (
        ORDER BY MAX(temperature) DESC
    ) AS temp_rank
FROM patient_experiment
GROUP BY patient;
```

## Minimal SQL Checklist

For the notebook material in this repository, the most useful SQL constructs are:

1. `SELECT`, `FROM`, `WHERE`, `ORDER BY`
2. `GROUP BY`, `HAVING`, `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
3. `INNER JOIN`, `LEFT JOIN`, `FULL OUTER JOIN`, `USING`
4. `CASE` and `COALESCE`
5. `CREATE VIEW`
6. `WITH` common table expressions
7. window functions with `OVER`, `PARTITION BY`, `RANK`, `LAG`, and running aggregates
8. `PIVOT` or conditional aggregation with `CASE`

## Best-Practice Summary

- In `pandas`, prefer high-level helpers such as `cut`, `pivot_table`, `merge`, datetime accessors, and categorical-aware operations when they fit the concept.
- In `polars`, prefer expression-based pipelines with `select`, `with_columns`, `filter`, `group_by`, `pivot`, and `over(...)` for grouped window-style work.
- In SQL, prefer declarative set-based constructs such as `CASE`, `JOIN`, `GROUP BY`, `HAVING`, CTEs, and window functions.
- Use the concept first, then choose the most idiomatic construct in each tool, even when the resulting code does not look structurally identical.
