# Brief Summary of Week 6

## Objective

Understand Spark architecture and perform efficient data processing using transformations, filtering, schema handling, and optimized file formats.

---

## What I Learned

* Understood Spark architecture and how it works.
* Learned about Lazy Evaluation and Directed Acyclic Graph (DAG).
* Read CSV and Parquet files in Spark.
* Performed filtering and selection operations on DataFrames.
* Modified DataFrames by renaming columns, casting data types, and adding new columns.
* Handled null values efficiently.
* Performed wide transformations and understood the concept of shuffle.
* Built a complete Spark ETL (Extract, Transform, Load) pipeline.
* Saved processed data into CSV and Parquet formats.
* Learned why `show()` is preferred over `collect()` for large datasets.

---

# Step 1 – Spark Architecture

## What is Spark Architecture?

Apache Spark follows a distributed computing architecture where the **Driver** creates the Spark application, the **Cluster Manager** allocates resources, and the **Executors** process data in parallel.

### Driver

The Driver is the main program responsible for creating the Spark application, scheduling tasks, and coordinating the overall execution of the application.

### Cluster Manager

The Cluster Manager manages the available cluster resources and allocates CPU and memory to the Spark application.

### Executors

Executors are worker processes that execute tasks assigned by the Driver and store processed data either in memory or on disk.

## Execution Modes

### Local Mode

Spark runs on a single machine. This mode is mainly used for learning, testing, and development.

### Cluster Mode

Spark runs on multiple machines where the Driver and Executors work together to process large datasets in parallel.

## Standard Code for Creating a Spark Session

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Assignment").getOrCreate()
```

### Conclusion

In this step, I created a `SparkSession`, which initializes the Spark application and serves as the entry point for performing DataFrame operations in PySpark.

---

# Step 2 – Lazy Evaluation and DAG (Lineage Graph)

## What is Lazy Evaluation?

Lazy Evaluation means that Spark does not execute transformations immediately. Instead, it waits until an action such as `show()`, `count()`, or `collect()` is called.

During this waiting period, Spark builds a **Directed Acyclic Graph (DAG)**, also known as the **Lineage Graph**, to optimize the execution plan and improve performance.

## Work Performed

* Learned how Spark postpones execution until an action is invoked.
* Understood how Spark builds a DAG to optimize task execution and eliminate unnecessary computations.

## Example

When operations like `filter()` or `select()` are applied, Spark does not process the data immediately. The transformations are executed only when an action such as `show()` or `count()` is called, resulting in more efficient execution.

---

# Step 3 – Reading Data from CSV and Parquet Files with Proper Schema Handling

## What is Reading Data?

Spark supports reading data from various file formats, including CSV and Parquet. Proper schema handling ensures that every column is assigned the correct data type, making data processing more accurate and efficient.

## Work Performed

* Created a `SparkSession` to initialize the Spark application.
* Loaded datasets from CSV and Parquet files.
* Used `header=True` and `inferSchema=True` to automatically detect column names and data types.
* Verified the schema using `printSchema()`.
* Displayed sample records using `show()`.

## Conclusion

* Successfully loaded CSV and Parquet files.
* Spark automatically inferred the schema.
* Displayed the dataset structure and sample records for further processing.

---

# Step 4 – Filtering and Selection

In this step, the dataset was filtered to retain only the records that satisfied specified conditions. After filtering, only the required columns were selected from the DataFrame. This reduced unnecessary data and improved processing efficiency.

## Conclusion

The DataFrame was successfully filtered using conditions such as:

* `Category == "Electronics"`
* `Status == "Completed" AND Amount > 1000`

Only the required columns (`id`, `price`, and `category`) were selected for further processing and analysis.

---

# Step 5 – Applying Transformations

In this step, I modified the DataFrame by renaming columns, changing data types, and adding new columns.

## Work Performed

* Renamed the `product_price` column to `price`.
* Converted the `price` column from **String** to **Double** using the `cast()` function.
* Created a new column named `final_price` using the `withColumn()` method.
* Calculated `final_price` by multiplying the base price by `1.18` to include tax.

---

# Step 6 – Handling Null Values

In this task, the dataset was cleaned by removing null values to improve data quality and avoid errors during analysis.

## Example

```python
# Remove rows containing null values
clean_df = df.dropna()
```

## Conclusion

Using `dropna()`, rows containing null values were removed successfully, resulting in a cleaner dataset for further processing.

---

# Step 7 – Wide Transformations and Performance Concepts (Shuffle and Predicate Pushdown)

In this task, I studied wide transformations, shuffle operations, and predicate pushdown.

Wide transformations, such as `groupBy()`, `join()`, and `distinct()`, require data to be redistributed across partitions. This redistribution process is called **shuffle**, where Spark transfers data between executors so that records with the same key are processed together.

Another important optimization technique is **Predicate Pushdown**, where Spark pushes filter conditions down to the data source (such as Parquet files). As a result, only the required records are read into memory, improving performance.

## Conclusion

* The `groupBy()` operation demonstrated a wide transformation involving a shuffle operation.
* The `filter()` operation demonstrated predicate pushdown, allowing Spark to read only the required records from supported formats like Parquet.

---

# Step 8 – Building a Complete Spark Data Pipeline

In this task, I developed a complete Spark ETL (Extract, Transform, Load) pipeline.

The pipeline followed these steps:

1. Read data from the source file.
2. Applied multiple transformations.
3. Filtered the required records.
4. Wrote the processed data to the output location.

This workflow demonstrated an efficient end-to-end Spark data processing pipeline.

---

# Step 9 – Saving Processed Data into CSV and Parquet Formats

After completing all transformations, the processed DataFrame was saved in both **CSV** and **Parquet** formats.

Saving data in these formats allows the processed dataset to be reused for future analysis and improves compatibility with different data processing systems.

---

# Step 10 – Why `show()` is Preferred Over `collect()` for Large Datasets

Both `show()` and `collect()` are Spark actions, but they serve different purposes.

* `show()` is used to display only a small number of rows (20 by default) from a DataFrame for quick inspection.
* `collect()` retrieves the entire dataset from all executors and transfers it to the Driver program.

For large datasets, `show()` is preferred because it consumes minimal memory and provides a quick preview of the data.

In contrast, `collect()` loads the complete dataset into the Driver's memory. If the dataset is very large, this may lead to excessive memory usage, poor performance, or even an **OutOfMemoryError**.

## Conclusion

Use `show()` for inspecting large datasets and reserve `collect()` only for small datasets where all records are required in the Driver program.
