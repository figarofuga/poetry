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
# usueful functions

# date_df = (pd.DataFrame(pd.date_range(start="2023-04-01", end="2024-03-31"), columns=["date"])
#            .assign(is_specialholiday = lambda dat:dat['date'].map(jpholiday.is_holiday).astype(int), 
#                       is_weekend = lambda dat:dat['date'].dt.day_name().isin(['Saturday', 'Sunday']).astype(int))
#                       .assign(is_holiday = lambda dat: np.where(dat['is_specialholiday'] + dat['is_weekend'] == 0, 0, 1))
#                       .filter(['date', 'is_holiday'])
#                       .assign(
#     workday = lambda dat: np.where(dat['is_holiday'] == 0, 1, 0), 
#     holiday_am = lambda dat: np.where(dat['is_holiday'] == 1, 1, 0),    
#     holiday_pm = lambda dat: np.where(dat['is_holiday'] == 1, 1, 0))
#     .melt(id_vars=['date', 'is_holiday'], var_name='work_name', value_vars=['workday', 'holiday_am', 'holiday_pm'])
#     .query('value == 1')
# )


# %%
# define values 
year_start = datetime(2022, 4, 1)
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
                   .with_columns([ pl.col('date_char').str.extract('(.*)(\\()', 1).str.strip().str.strptime(pl.Date,fmt='%Y/%m/%d ').alias("date")])
                   .with_row_count(name='id'))

request_shift = form_answer_mod.filter(pl.col("value") == 2).sort("date")

request_duplicate = request_shift.filter(pl.col("date").is_duplicated())

request_unique = request_shift.filter(pl.col("date").is_unique())

# .pivot(index=['date_char', 'date'],values='value', columns=['name'])

# %% 
# we made record shift

# Define a function to filter numeric columns
#def is_numeric(col: pl.Expr) -> bool:
#    return col.dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]

# Group by 'sex' and sum across all numeric columns
#numeric_columns = [col for col in pbc.columns if is_numeric(pbc[col])]
#result = pbc.groupby("sex").agg([pl.col(col).sum().alias(col) for col in numeric_columns])

pasthistory = (pl.DataFrame(record_shift).rename({'Unnamed: 0': 'year', 'Unnamed: 1': 'month'})
               .with_column(
    (pl.col('year').cast(pl.Utf8) + '-' + pl.col('month').cast(pl.Utf8) + '-1').alias('date'))
               .with_column(
    pl.col('date').str.strip().str.strptime(pl.Date, fmt='%Y-%m-%d')
               )
               .with_column(
    (pl.col('date')-pl.duration(days=1))
               )
               .filter(pl.col('date').is_between(year_start, stop))
               .fill_null(0)
               .groupby('シフト種類')
               .agg(
    [pl.sum(pl.col('河瀬')).alias('河瀬')]
               )
               )
               


# %%
# form_answer_mod = (pl.DataFrame(form_answer)
#                    .rename({'0': 'input_time', '1': 'name', '2': 'date', '3': 'date_type', '4': 'value'})
#                    .select(['name', 'date', 'date_type', 'value'])
#                    .rename({"date": "date_char"})
#                    .with_columns([pl.col('date_char').str.extract('(.*)(\\()', 1).str.strip().str.strptime(pl.Date,fmt='%Y/%m/%d ').alias("date")])
#                    .pivot(index=['date_char', 'date'],values='value', columns=['name'])
#                    .filter(pl.col("date").is_between(start, stop))
#                    .to_pandas()
#                    .assign(
#         is_specialholiday = lambda dat:dat['date'].map(jpholiday.is_holiday).astype(int), 
#         is_weekend = lambda dat:dat['date'].dt.day_name().isin(['Saturday', 'Sunday']).astype(int))
#           .assign(is_holiday = lambda dat: np.where(dat['is_specialholiday'] + dat['is_weekend'] == 0, 0, 1)))

