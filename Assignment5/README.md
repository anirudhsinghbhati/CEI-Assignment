# Week 5 - Apache Spark Summary

## Topics Covered

### 1. MapReduce vs Spark
- MapReduce relies heavily on disk I/O.
- Spark uses in-memory processing, making it much faster.
- Spark is better suited for iterative algorithms, real-time analytics, and machine learning workloads.

### 2. In-Memory Computing
- Spark stores intermediate data in RAM.
- Reduces repeated disk reads and writes.
- Improves performance for iterative computations and data analysis.

### 3. Data Cleaning
- Remove duplicate records using `dropDuplicates()`.
- Handle missing values using:
  - `na.drop()` to remove null rows.
  - `na.fill()` to replace null values.
- Filter invalid records using conditions.

### 4. DataFrame Immutability
- Spark DataFrames are immutable.
- Operations such as filtering, renaming, and dropping columns create new DataFrames instead of modifying existing ones.

### 5. Filtering and Aggregations
- Filter data using conditions with `filter()`.
- Perform aggregations using:
  - `groupBy()`
  - `count()`
  - `sum()`
  - `avg()`
  - `agg()`

### 6. Shuffle Operations
- Occur during grouping, joins, and aggregations.
- Redistribute data across partitions.
- Considered a wide transformation because data moves between executors.

### 7. Schema Management
- `inferSchema=true` automatically detects data types.
- Inconsistent or messy data may result in incorrect schema detection.
- Explicit schemas are preferred for production workloads.

### 8. Common Data Processing Pipeline
1. Remove duplicates.
2. Handle null values.
3. Filter required records.
4. Group data by key columns.
5. Perform aggregations and generate final results.

## Key Spark Functions Learned

```python
dropDuplicates()
filter()
groupBy()
agg()
count()
sum()
avg()
na.drop()
na.fill()
withColumn()
withColumnRenamed()
cast()
```

## Learning Outcome
By the end of Week 5, I should understand how to clean datasets, handle null values, remove duplicates, perform aggregations, manage schemas, and build efficient Spark data processing pipelines.
