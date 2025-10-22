# ==== 1) Basic Libraries ====
import os  # Handle file paths
import re  # Regular expressions, used for field name recognition
import json  # Save field matching logs
import numpy as np  # Numerical computation
import pandas as pd  # Main library for data processing
from datetime import datetime  # Handle date operations
from textwrap import dedent  # Nicely format printed text

# ===== 2011 Simplified Reading =====
import pandas as pd
import os

# Get current script directory
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "2011年个人数据(STATA).dta")

# Read file
df = pd.read_stata(file_path, convert_categoricals=False)
print(f"✔ Loaded {file_path}")
# Shanghai and Beijing Dummy
df["city_clean"] = df["city"].astype(str).str.strip()
df["is_beijing"] = (df["city_clean"] == "北京市").astype(int)
df["is_shanghai"] = (df["city_clean"] == "上海市").astype(int)
# Gender Dummy Male == 1 Female == 0
df["male"] = (df["q101b1"] == 1).astype(int)
print(df[["q101b1", "male"]].head(10))
# Age
df["q101c1"] = df["q101c1"].astype(str).str.strip()
df["birth_year"] = df["q101c1"].str[:4]
df["birth_year"] = pd.to_numeric(df["birth_year"], errors="coerce")
df["age"] = 2011 - df["birth_year"]
df.loc[(df["age"] < 0) | (df["age"] > 120), "age"] = pd.NA  # Remove abnormal ages
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["age"] = df["age"].round(0).astype("Int64")

# Hukou residence renaming  # Whether to divide by East/Central/West regions; dummy generation to be decided
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
first_true_pos = edu_dummies.eq(1).idxmax(axis=1)                 # The first column with 1 per row
has_any_true   = edu_dummies.eq(1).any(axis=1)                    # Whether there is at least one 1
for col in ["high_school", "junior_college", "bachelor", "graduate"]:
    df[col] = np.where(has_any_true & (first_true_pos != col), 0, df[col]).astype("int8")
df = df.copy()
print(df[["q101g1","high_school","junior_college","bachelor","graduate"]].head(10))
# Hukou: Agricultural/Non-agricultural
df["q101h1"] = pd.to_numeric(df["q101h1"], errors="coerce")
df["rural"] = (df["q101h1"] == 1).astype(int)
print(df[["q101h1","rural"]].head(10))
# Migration or not
df["q101i1"] = pd.to_numeric(df["q101i1"], errors="coerce")
df["Migrate"] = (df["q101i1"] != 4).astype(int)  # q101i1 == 4 means no migration
print(df[["q101i1","Migrate"]].head(10))
# 1 Inter-provincial migration
df["Migrate_1"] = (df["q101i1"] == 1).astype(int)
# 2 Intra-provincial inter-city
df["Migrate_2"] = (df["q101i1"] == 2).astype(int)
# 3 Intra-city inter-county
df["Migrate_3"] = (df["q101i1"] == 3).astype(int)
#
# Arrival year
df["q101j1"] = df["q101j1"].astype(str).str.strip()
df["migration_year"] = df["q101j1"].str[:4]
# Years since migration
df["migration_year"] = pd.to_numeric(df["migration_year"], errors="coerce")
df["migration_interval"] = 2011 - df["migration_year"]
# Marriage  # Missing values set to 0
df["marriage"] = (df["q101k2"] == 2).astype(int)
# Employment  # Missing values set to 0
df["employed"] = (df["q101l2"] == 1).astype(int)
print(df[["q101k2","marriage", "q101l2","employed"]].head(10))
# Handle missing values and winsorization (95%) for income/expenditure-related numeric variables
df["income_total_m"] = df["q105"]
df["exp_total_m"] = df["q103"]
df["food_exp_m"] = df["q102"]
df["income_to_home"] = df["q104"]
df["rent_m"] = df["q302"]
target_vars = [
    "income_total_m",  # Total monthly income
    "exp_total_m",     # Total monthly expenditure
    "food_exp_m",      # Monthly food expenditure
    "income_to_home",  # Money sent home last year
    "rent_m",          # Rent
]
# Winsorization function
def winsorize_95(series):
    """Winsorize numerical variables at 95th percentile (upper cap) and set missing values to 0"""
    s = pd.to_numeric(series, errors="coerce")
    # Compute 95th percentile (excluding NaN)
    upper = s.quantile(0.95)
    s = np.where(s > upper, upper, s)
    s = np.nan_to_num(s, nan=0.0)
    return s

# Winsorize + fill missing values
for col in target_vars:
    if col in df.columns:
        df[col + "_win"] = winsorize_95(df[col])  # Create new column with _win suffix
        print(f"Completed winsorization and filling missing values for {col}.")
    else:
        print(f"Column not found: {col}")

print(df[[c for c in df.columns if c.endswith('_win')]].describe())
# Employment classification
def classify_employment(row):
    q204, q207 = row["q204"], row["q207"]
    # Government/public institutions
    if q204 in [2, 3, 4]:  # 2=Gov’t, 3=State-owned, 4=Collective enterprise
        return "public_sector"
    # Private/foreign enterprises
    elif q204 in [1, 6, 7, 8, 9, 10]:  # 1=Land contractor, 6=Private, 7–10=Foreign-related
        return "private_enterprise"
    # Self-employed
    elif q207 in [2]:  # 4=self-employed, 5=self-hired
        return "self_employed"
    # Employer
    elif q207 == 1:
        return "employer"
    # Family worker
    elif q207 == 3:
        return "family_worker"
    # Casual worker
    elif q207 in [3, 5, 4]:
        return "casual_worker"
    else:
        return "other"

df["employment_category"] = df.apply(classify_employment, axis=1)
# Merge into large groups: formal, informal, self-employed
df["employment_group"] = df["employment_category"].map({
    "public_sector": "formal",
    "private_enterprise": "formal",
    "self_employed": "self_employed",
    "employer": "self_employed",
    "family_worker": "informal",
    "casual_worker": "informal",
    "other": "informal"
})
# Work stress / rhythm
# How many hours per week last month
df["workdays_w"] = pd.to_numeric(df["q208"], errors="coerce")
df["workhours_d"] = pd.to_numeric(df["q209"], errors="coerce")
df["hours_per_week"] = df["workdays_w"] * df["workhours_d"]
df["hours_per_week_filled"] = df["hours_per_week"].fillna(0)
print(df[["workdays_w", "workhours_d", "hours_per_week", "hours_per_week_filled"]].head(10))
# Years since marriage
df["q401"] = df["q401"].astype(str).str.strip()
df["marriage_year"] = df["q401"].str[:4]
df["marriage_year"] = pd.to_numeric(df["marriage_year"], errors="coerce")
df["length_marriage"] = 2011 - df["marriage_year"]
df["length_marriage"] = df["length_marriage"].fillna(0)
# Here, marriage length = 0 doesn’t necessarily mean married; should be filtered by marriage variable if needed
# Number of children
df["kids_number"] = df["q402"]
df["kids_number"] = df["kids_number"].fillna(0)
# Child’s birthplace
df["birth_here"] = (df["q40331"] == 1).astype(int)
print(df[["q40331","birth_here"]].head(10))
# Local social insurance coverage: overview — most migrants lack full “five insurances and one fund” (only 261 people have full coverage)
df["Pension_Insurance"] = (df["q502a"] == 1).astype(int)
df["Pension_Insurance"] = df["Pension_Insurance"].fillna(0)
df["Medical_Insurance"] = (df["q502b"] == 1).astype(int)
df["Medical_Insurance"] = df["Medical_Insurance"].fillna(0)
df["Work_Insurance"] = (df["q502c"] == 1).astype(int)
df["Work_Insurance"] = df["Work_Insurance"].fillna(0)
df["Unemploy_Insurance"] = (df["q502d"] == 1).astype(int)
df["Unemploy_Insurance"] = df["Unemploy_Insurance"].fillna(0)
df["Maternity_Insurance"] = (df["q502e"] == 1).astype(int)
df["Maternity_Insurance"] = df["Maternity_Insurance"].fillna(0)
df["Housing_Fund"] = (df["q502f"] == 1).astype(int)
df["Housing_Fund"] = df["Housing_Fund"].fillna(0)

# Happiness index (0–17, higher = happier), average of five questions, last one reversed
df["Happiness"] = df["q5101"] + df["q5102"] + df["q5103"] + df["q5104"] - df["q5105"]
df["Happiness"] = df["Happiness"].fillna(0)
print(df[["Happiness"]].head(10))

import os

# Get current script directory
root_dir = os.path.dirname(__file__)

# Compose output path under root directory
output_path = os.path.join(root_dir, "clean_2011.csv")

# Save CSV
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"✔ Saved to: {output_path}")
