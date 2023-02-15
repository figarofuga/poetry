# %%
import numpy as np
import pandas as pd
import polars as pl

# %%
df = pd.read_excel('to_niimi.xlsx')
dfl = pl.DataFrame(df)

# %%
df_null = dfl[:, [(s.null_count() == dfl.height) for s in dfl]]

df_an = (dfl[:, [not (s.null_count() == dfl.height) for s in dfl]]
         .rename({'2022/04/01 (金)\n平日夜間': 'date',
                    '平日夜間': 'type_date'})
         .select([pl.col("date").str.extract("(.*)(\\()", 1).str.strptime(pl.Date, fmt='%Y/%m/%d '),
                 pl.col("type_date"),
                 pl.col(pl.Float64).map(np.floor)])
         .with_column(
                 pl.when(pl.col("type_date") == "平日夜間").then("weekday").when(pl.col("type_date") == "休日午前").then("weekend_am").otherwise("weekend_night").alias("type_date"))
         .with_row_count())

# %% 
weights = {"weekday": 1, "weekend_am": 1, "weekend_night": 2}

# %% [Markdown]
# The range of numbers are -1 to 2
# %%
import pulp


# %%

