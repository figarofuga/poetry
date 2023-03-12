# %%
import numpy as np
import pandas as pd
import polars as pl
from datetime import datetime
from dateutil.relativedelta import relativedelta
import itertools
import pprint
import jpholiday
# %%
# define values 
start = datetime(2022, 5, 1)
stop = start + relativedelta(months=1)


# %%
# tmp_df = (pd.DataFrame(pd.date_range(start="2023-02-01", end="2024-03-31"), columns=["date"])
#           .assign(person1 = np.nan, 
#                   person2 = np.nan))

# tmp_df.to_csv("hosp_shift2.csv", index=False)

oncall_member = pd.read_excel("oncall_shift.xlsx", sheet_name='オンコール名簿', index_col=None).loc[:, '名前'].to_list()

record_shift = pd.read_excel("oncall_shift.xlsx", sheet_name='統計①', index_col=None)


record_shift2 = pd.read_excel("oncall_shift.xlsx", sheet_name='統計②', index_col=None)

zantei_shift = pd.read_excel("oncall_shift.xlsx", sheet_name='暫定シフト表', index_col=None)

form_answer = pd.read_excel("oncall_shift.xlsx", sheet_name='フォーム回答', index_col=None, header=None)

hosp_shift = (pd.read_csv("hosp_shift.csv", parse_dates=['date'])
              .assign(is_specialholiday = lambda dat:dat['date'].map(jpholiday.is_holiday).astype(int), 
                      is_weekend = lambda dat:dat['date'].dt.day_name().isin(['Saturday', 'Sunday']).astype(int))
              .assign(is_holiday = lambda dat: np.where(dat['is_specialholiday'] + dat['is_weekend'] == 0, 0, 1))

)

# %%
# modify dataframes

form_answer_mod = (pl.DataFrame(form_answer)
                   .rename({'0': 'input_time', '1': 'name', '2': 'date', '3': 'date_type', '4': 'value'})
                   .select(['name', 'date', 'date_type', 'value'])
                   .with_columns([pl.col('date').str.extract('(.*)(\\()', 1).str.strip().str.strptime(pl.Date,fmt='%Y/%m/%d ').alias("date_char")]))

# %%

df_an = (dfl.rename({'2022/04/01 (金)\n平日夜間': 'date',
                '平日夜間': 'type_date'})
       .with_columns(
               [pl.col(pl.Float32).map(np.floor).keep_name(),
               pl.col("date").str.extract("(.*)(\\()", 1).str.strip().alias("date_char")])
       .with_columns([ 
               pl.col("date_char").str.strptime(pl.Date, fmt='%Y/%m/%d ').alias("date"), 
               pl.when(pl.col("type_date") == "平日夜間").then("weekday").when(pl.col("type_date") == "休日午前").then("weekend_am").otherwise("weekend_night").alias("type_date"), 
               pl.when(pl.col("type_date") == "休日午後").then(pl.col("date_char")+"_pm").when(pl.col("type_date") == "休日午前").then(pl.col("date_char")+"_am").otherwise(pl.col("date_char")).str.strip().alias("date_list")
               ])
               .with_row_count(name="row_num"))
         
# %%
# define duration

ranged_df = (df_an.filter(
    pl.col("date").is_between(start,stop),
))

df_all_null = ranged_df[:, [(s.null_count() == ranged_df.height) for s in ranged_df]]

df_any_null = ranged_df[:, [s.null_count() > 0 for s in ranged_df]]

df_full = ranged_df[:, [s.null_count() == 0 for s in ranged_df]]

df_any_val = ranged_df[:, [not s.null_count() == ranged_df.height for s in ranged_df]]
# %%

def get_tuple(colname): 
        mini_dat = (df_any_val.select(["row_num", colname]).filter(pl.col(colname) == -1.0))
        row_list = [(colname, mini_dat[i, "row_num"]) for i in range(len(mini_dat))]
        return row_list
        

# %% 
