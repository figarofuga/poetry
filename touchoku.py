#%% 
import numpy as np
import pandas as pd
import polars as pl
#%%
df = pd.read_excel('to_niimi.xlsx')
dfl = pl.DataFrame(df)
# %%
dfl.head()

# %%
df_an = (dfl.rename({'2022/04/01 (金)\n平日夜間': 'date', 
                    '平日夜間': 'type_date'}).
         select([pl.col("date").str.extract("(.*)(\\()", 1).str.strptime(pl.Date, fmt='%Y/%m/%d '), 
                 pl.col("type_date"),
                 pl.col(pl.Float64).map(np.floor)]))


# %%
