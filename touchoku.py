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
df_an = dfl.select([pl.col(pl.Float64).map(np.floor)]).head()
# %%
