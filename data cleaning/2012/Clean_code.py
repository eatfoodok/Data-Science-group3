# ==== 1) Basic Libraries ====
import os  # Handle file paths
import re  # Regular expressions, used for field name recognition
import json  # Save field matching logs
import numpy as np  # Numerical computation
import pandas as pd  # Main library for data processing
from datetime import datetime  # Handle date operations
from textwrap import dedent  # Nicely format printed text

# ===== 2012 Simplified Reading =====
import pandas as pd
import os

# Get current script directory
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "2012年 个人数据 【全】.dta")

# Read file
df = pd.read_stata(file_path, convert_categoricals=False)
print(f"✔ Loaded {file_path}")
# ==== Standardize variable names: rename 2012 fields to match the 2011 code naming conventions ====
rename_map = {
    # —— 101 (aligned with 2011 code usage) ——
    "gender_1":      "q101b1",   # Gender
    "birt_date_1":   "q101c1",   # Birth year/month
    "resi_place_1":  "q101e1",   # Hukou location (used for hs_residence)
    "nation_1":      "q101f1",   # Ethnicity (used as is_han==1)
    "edu_status_1":  "q101g1",   # Education level (used for education dummies)
    "acc_nature_1":  "q101h1",   # Hukou type (used for rural)
    "flo_rage_1":    "q101i1",   # Migration range (used for Migrate/1/2)
    "flo_time_1":    "q101j1",   # Year of migration (first 4 digits)
    "mar_status_2":  "q101k2",   # Marital status (spouse)
    "emp_status_2":  "q101l2",   # Employment status (spouse)

    # —— Employment/Residence (201–214), based on usage in classification function ——
    "fir_away":      "q201",
    "employment":    "q202",
    "industry":      "q203",
    "unit_quality":  "q204",     # Used in classification logic for organization type
    "emly_ident":    "q207",     # Used in classification logic for employer/self-employed/family worker
    "aver_days":     "q208",
    "aver_hours":    "q209",
    "time_unemploy": "q210",
    "housetype":     "q211",
    "localMIUW":     "q212",
    "reialMIUW":     "q213",

    # —— Marriage & Fertility (used in later code) ——
    "firmarr_time":  "q401",     # Year of first marriage
    "fer_numb":      "q402",     # Number of children
    "bir_place_1":   "q40331",   # Birthplace of first child

    # —— Income & Expenditure (directly used as q102/103/104/105) ——
    "cost_m":        "q103",     # Monthly total expenditure
    "money_home":    "q104",     # Remittance last year
    "famincom_m":    "q105",     # Monthly total income

    # Food expenditure: 2012 split into two columns, map A→q102, B→q102b, then merge into q102
    "foodcost_m":    "q102",     # A: self-paid
    "foodcost_m2":   "q102b",    # B: employer-provided (to be merged into q102)

    # q302 used for rent in your 2011 code (df['rent_m']=df['q302']), so map rent here
    "rent_m":        "q302",

    # —— Happiness index (directly used as q5101~q5105) ——
    "love_city":       "q5101",
    "atte_change":     "q5102",
    "loca_integrate":  "q5103",
    "loca_accept":     "q5104",
    "loca_despise":    "q5105",
}

df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# Merge food expenditure into q102 (A+B)
if "q102b" in df.columns:
    df["q102"] = pd.to_numeric(df.get("q102"), errors="coerce").fillna(0) + \
                 pd.to_numeric(df.get("q102b"), errors="coerce").fillna(0)

# Ensure existence of insurance columns q502a–q502f (may not exist in 2012 data)
for c in ["q502a","q502b","q502c","q502d","q502e","q502f"]:
    if c not in df.columns:
        df[c] = np.nan

# Execute renaming
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# Merge food expenditure into q102
# === Merge food expenditure into q102 (A self-paid + B employer-provided) ===
# Merge process
if "foodcost_m" in df.columns or "q102a" in df.columns:
    a = df.get("q102a", df.get("foodcost_m"))
    b = df.get("q102b", df.get("foodcost_m2"))
    a = pd.to_numeric(a, errors="coerce").fillna(0)
    b = pd.to_numeric(b, errors="coerce").fillna(0)
    df["q102"] = a + b
else:
    df["q102"] = np.nan


# Keep rent field as rent_m for derived calculations later
if "q302_rent" in df.columns:
    df["rent_m"] = pd.to_numeric(df["q302_rent"], errors="coerce")

print("✅ Completed 2012→2011 field renaming and unification.")


# Shanghai & Beijing Dummy
for cand in ["city", "city_name", "pro_name"]:
    if cand in df.columns:
        df["city_clean"] = df[cand].astype(str).str.strip()
        break
else:
    raise KeyError("No city / city_name / pro_name field found in the current file")

df["is_beijing"] = df["city_clean"].str.contains("北京").astype(int)
df["is_shanghai"] = df["city_clean"].str.contains("上海").astype(int)

# Gender Dummy Male == 1 Female == 0
sex_col = None
for cand in ["q101b1", "gender_1"]:
    if cand in df.columns:
        sex_col = cand
        break
if sex_col is None:
    raise KeyError("Gender field not found (q101b1 or gender_1)")

df["male"] = (df[sex_col] == 1).astype(int)

print(df[[sex_col, "male"]].head(10))

# Age
birth_col = "q101c1" if "q101c1" in df.columns else "birt_date_1"
df[birth_col] = df[birth_col].astype(str).str.strip()
df["birth_year"] = df[birth_col].str[:4].astype(float)

df["birth_year"] = df["q101c1"].str[:4]
df["birth_year"] = pd.to_numeric(df["birth_year"], errors="coerce")
df["age"] = 2011 - df["birth_year"]
df.loc[(df["age"] < 0) | (df["age"] > 120), "age"] = pd.NA  # Remove abnormal ages
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["age"] = df["age"].round(0).astype("Int64")

# Hukou residence renaming  # Whether to divide by region (East/Central/West) — dummy generation pending
df["hs_residence"] = df["q101e1"]
# Ethnicity Han == 1, Others == 0
df["is_han"] = (df["q101f1"] == 1).astype(int)
# Education level
df["q101g1"] = pd.to_numeric(df["q101g1"], errors="coerce")
mask_high  = df["q101g1"].isin([1, 2, 3, 4])     # High school or below
mask_jc    = df["q101g1"].isin([5, 6])           # Junior college
mask_ba    = df["q101g1"].eq(7)                  # Bachelor
mask_grad  = df["q101g1"].eq(8)                  # Graduate or above
edu_dummies = pd.DataFrame({
    "high_school":      mask_high.astype("int8"),
    "junior_college":   mask_jc.astype("int8"),
    "bachelor":         mask_ba.astype("int8"),
    "graduate":         mask_grad.astype("int8"),
}, index=df.index)
df = pd.concat([df, edu_dummies], axis=1)
first_true_pos = edu_dummies.eq(1).idxmax(axis=1)                 # Column name of first 1 per row
has_any_true   = edu_dummies.eq(1).any(axis=1)                    # Whether at least one 1 exists
for col in ["high_school", "junior_college", "bachelor", "graduate"]:
    df[col] = np.where(has_any_true & (first_true_pos != col), 0, df[col]).astype("int8")
df = df.copy()
print(df[["q101g1","high_school","junior_college","bachelor","graduate"]].head(10))
# Agricultural/Non-agricultural Hukou
df["q101h1"] = pd.to_numeric(df["q101h1"], errors="coerce")
df["rural"] = (df["q101h1"] == 1).astype(int)
print(df[["q101h1","rural"]].head(10))
# Migration or not
df["q101i1"] = pd.to_numeric(df["q101i1"], errors="coerce")
df["Migrate"] = (df["q101i1"] != 4).astype(int)  # q101i1 == 4 means not migrated
print(df[["q101i1","Migrate"]].head(10))
# 1 Inter-provincial migration
df["Migrate_1"] = (df["q101i1"] == 1).astype(int)
# 2 Intra-provincial inter-city
df["Migrate_2"] = (df["q101i1"] == 2).astype(int)
# 3 Intra-city inter-county
df["Migrate_3"] = (df["q101i1"] == 3).astype(int)
#
# Time of arrival:
df["q101j1"] = df["q101j1"].astype(str).str.strip()
df["migration_year"] = df["q101j1"].str[:4]
# Years since arrival
df["migration_year"] = pd.to_numeric(df["migration_year"], errors="coerce")
df["migration_interval"] = 2011 - df["migration_year"]
# Marriage  # Missing values unified to 0
df["marriage"] = (df["q101k2"] == 2).astype(int)
# Employment  # Missing values unified to 0
df["employed"] = (df["q101l2"] == 1).astype(int)
print(df[["q101k2"]()]()
