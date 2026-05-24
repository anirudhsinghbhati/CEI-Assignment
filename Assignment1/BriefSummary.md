# Brief Summary

- Loaded the `Combined_dataset.csv` file into a Pandas DataFrame named `df`.

- Performed initial data exploration using:
  - `df.head()`
  - `df.tail()`
  - `df.describe()`
  - `df.shape`
  - `df.dtypes`

- Cleaned and handled missing data:
  - Removed currency symbols and commas from the `final_price` column.
  - Converted `final_price` to `float` data type.
  - Filled missing values in the `discount` column with `0`.
  - Dropped unnecessary or highly incomplete columns:
    - `what_customers_said`
    - `seller_name`
    - `videos`
    - `seller_information`
    - `variations`

- Performed basic data operations:
  - Filtered products where:
    - `rating > 4.5`
    - `discount > 70`
    - `final_price < 10000`
  - Stored filtered results in `filtered_df`.

- Selected important columns into a new DataFrame `df_selected`:
  - `product_id`
  - `title`
  - `final_price`
  - `rating`
  - `category`
  - `initial_price`
  - `discount`

- Checked duplicate records using:
  - `df.duplicated().sum()`

- Removed duplicate rows using:
  - `df.drop_duplicates()`

- Created a new derived column:
  - `potential_discount_amount = initial_price * (discount / 100)`

- Saved the cleaned and processed dataset as:
  - `cleaned_product_data.csv`

- Successfully completed data cleaning, preprocessing, filtering, and feature engineering tasks using Pandas in Jupyter Notebook.
