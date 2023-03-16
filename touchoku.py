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
                   .rename({"date": "date_char"})
                   .with_columns([pl.col('date_char').str.extract('(.*)(\\()', 1).str.strip().str.strptime(pl.Date,fmt='%Y/%m/%d ').alias("date")])
                   .pivot(index=['date_char', 'date'],values='value', columns=['name'])
                   .filter(pl.col("date").is_between(start, stop))
                   .to_pandas()
                   .assign(
        is_specialholiday = lambda dat:dat['date'].map(jpholiday.is_holiday).astype(int), 
        is_weekend = lambda dat:dat['date'].dt.day_name().isin(['Saturday', 'Sunday']).astype(int))
          .assign(is_holiday = lambda dat: np.where(dat['is_specialholiday'] + dat['is_weekend'] == 0, 0, 1)))

