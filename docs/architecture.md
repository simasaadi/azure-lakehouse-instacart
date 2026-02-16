\# Architecture (high level)



Kaggle Instacart CSVs

&nbsp;       |

&nbsp;       v

DuckDB (warehouse/instacart\_{DATA\_MODE}.duckdb)

&nbsp;       |

&nbsp;       +--> Silver (data/silver\_parquet/)

&nbsp;       |        - dim\_departments

&nbsp;       |        - dim\_aisles

&nbsp;       |        - dim\_products

&nbsp;       |        - fct\_orders

&nbsp;       |        - fct\_order\_products

&nbsp;       |

&nbsp;       +--> Gold (data/gold\_parquet/)

&nbsp;                - mart\_customer

&nbsp;                - mart\_product

&nbsp;                - mart\_demand\_profile



Cloud emulator path (Azure-compatible):

Gold Parquet -> Azurite container lakehouse/gold/\*

&nbsp;       |

&nbsp;       v

Authenticated download (Azure SDK) -> DuckDB query (scripts/07\_query\_gold\_from\_blob.py)



