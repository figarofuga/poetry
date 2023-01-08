#%% 
import pandas as pd
import polars as pl
#%%
df = pd.read_excel('to_niimi.xlsx')
dfl = pl.DataFrame(df)
# %%
dfl.head()
# %%

# %%
