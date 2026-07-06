# Delta Lake Assignment — Incremental Load & SCD using MERGE

A Delta Lake + PySpark pipeline that loads customer data, cleans it, and applies incremental updates using MERGE (SCD logic).

## Project Structure

```
week 7
│
├── data/
│   ├── customer_master.csv
│   └── customer_incremental.csv
│
├── notebooks/
│   └── delta_scd_assignment.ipynb
│
├── screenshots/
│   ├── data_loading/
│   ├── data_cleaning/
│   ├── scd1
│   ├── validation/
│   └── final_output/
│
├── report- 
│   └── Report + Detailed Summary.pdf
│
└── README.md
```

## Pipeline Steps

1. **Load** — CSV read and saved as a Delta table.
2. **Clean** — Nulls and duplicates removed.
3. **Incremental Load** — Second CSV read for new/updated records.
4. **Merge** — MERGE updates matched rows, inserts new ones.
5. **Validate** — Row count + duplicate checks confirm success.
6. **Final Output** — Updated Delta table displayed.

## Requirements

- Databricks / Spark with Delta Lake
- PySpark, `delta-spark`

## How to Run

1. Add CSVs to `data/`.
2. Open the notebook in Databricks.
3. Update file paths if needed.
4. Run all cells top to bottom.

## Conclusion

Delta Lake's MERGE enables reliable incremental updates in a single atomic operation — ideal for SCD use cases.
