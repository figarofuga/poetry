# %%
import numpy as np
import pandas as pd
import polars as pl

# %%
df = pd.read_excel("to_niimi.xlsx")
dfl = pl.DataFrame(df)
# %%
df_all_null = dfl[:, [(s.null_count() == dfl.height) for s in dfl]]

df_prep = (dfl[:, [not (s.null_count() == dfl.height) for s in dfl]]
         .rename({'2022/04/01 (金)\n平日夜間': 'date',
                    '平日夜間': 'type_date'})
         .select([pl.col("date").str.extract("(.*)(\\()", 1).str.strptime(pl.Date, fmt='%Y/%m/%d '),
                 pl.col("type_date"),
                 pl.col(pl.Float64).map(np.floor)])
         .with_column(
                 pl.when(pl.col("type_date") == "平日夜間").then("weekday").when(pl.col("type_date") == "休日午前").then("weekend_am").otherwise("weekend_night").alias("type_date"))
         )


df_any_null = df_prep[:, [s.null_count() > 0 for s in df_prep]].with_row_count(name="row_num")

df_nonnull = df_prep[:, [s.null_count() == 0 for s in df_prep]].with_row_count(name="row_num")

df_an = df_any_null.join(df_nonnull, on="row_num", how="left")
# %% 
weights = {"weekday": 1, "weekend_am": 1, "weekend_night": 2}

# %% [Markdown]
# The range of numbers are -1 to 2
# %%
import pulp
# 問題の定義
problem = pulp.LpProblem(name="Tochoku", sense=pulp.LpMinimize)

# %% [Markdown]
# sequential work should be avoided
# Doctors at -1 should be avoided
# Each workers load should be equal

# 変数の定義
A = pulp.LpVariable(name = "A", lowBound = 0, cat="Integer")
B = pulp.LpVariable(name = "B", lowBound = 0, cat="Integer")
C = pulp.LpVariable(name = "C", lowBound = 0, cat="Integer")

# 目的関数
problem += 20*A + 12*B + 18*C

# 制約条件の定義
problem += 22*A + 13*B + 17*C >= 200
problem += 20*A + 30*B + 5*C >= 200
problem += 10*A + 5*B + 12*C >= 100

# 解く
status = problem.solve()
print(pulp.LpStatus[status])

# 結果表示
print("Result")
print("A:", A.value())
print("B:", B.value())
print("C:", C.value())
