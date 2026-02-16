\# Architecture (high level)



Kaggle Instacart CSVs

|

v

DuckDB (warehouse/instacart\_{DATA\_MODE}.duckdb)

|

+--> Silver (data/silver\_parquet/)

|    - dim\_departments

|    - dim\_aisles

|    - dim\_products

|    - fct\_orders

|    - fct\_order\_products

|

+--> Gold (data/gold\_parquet/)

&nbsp;    - mart\_customer

&nbsp;    - mart\_product

&nbsp;    - mart\_demand\_profile



Cloud emulator path (Azure-compatible):

Gold Parquet -> Azurite container lakehouse/gold/\*

|

v

Authenticated download (Azure SDK) -> DuckDB query (scripts/07\_query\_gold\_from\_blob.py)



