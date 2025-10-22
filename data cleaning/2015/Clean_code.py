# ==== 1) Basic Libraries ====
import os  # Handle file paths
import re  # Regular expressions, used for field name recognition
import json  # Save field matching logs
import numpy as np  # Numerical computation
import pandas as pd  # Main library for data processing
from datetime import datetime  # Handle date operations
from textwrap import dedent  # Format text neatly

# ===== 2015 Simplified Reading =====
import pandas as pd
import os

# Get current script directory
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "a卷(STATA).dta")

# Read file
df = pd.read_stata(file_path, convert_categoricals=False)
print(f"✔ Loaded {file_path}")
# ===================== 2015 Adaptation Layer (based on provided column headers) =====================
import numpy as np
import pandas as pd

BASE_YEAR = 2015

# 1) Unified renaming: map provided column names → expected names in legacy code
rename_map_2015 = {
    # 101 (Respondent = Person 1): already named as q101*, mostly consistent
    # Only rename columns that differ or are required later

    # —— Income/expenditure: legacy code uses q102/103/104/105 and treats q302 as “rent” ——
    "Q102":  "q102",      # Household monthly food expenditure (if Q1021/Q1022 exist, will merge)
    "Q1021": "q102_1",
    "Q1022": "q102_2",
    "Q103":  "q103",      # Household total monthly expenditure
    "Q104":  "q302",      # Housing (rent/mortgage), legacy code uses q302 as rent
    "Q105":  "q105",      # Household total monthly income
    "Q106":  "q106",      # Possibly disposable or other income, kept for potential later use

    # —— Employment grouping: classification uses q204 (organization type) and q207 (employment identity) ——
    # 2015 headers use Q205 (organization type), Q206 (employment identity), Q208/Q209 (working hours)
    "Q205":  "q204",      # Organization type: government/public/state/collective/private/foreign/joint/self-employed...
    "Q206":  "q207",      # Employment identity: employee/employer/self-employed/family helper...
    "Q208":  "q208",      # Workdays per week
    "Q209":  "q209",      # Working hours per day

    # —— First migration from hukou location (not used, but harmless to keep) ——
    "Q201Y": "q201y",
    "Q201M": "q201m",

    # —— Marriage & fertility: legacy code uses q401 (first marriage “YYYYMM”), q402 (children count), q40331 (first child birthplace) ——
    "Q401":  "q401",      # If already combined “YYYYMM”, can be used directly
    "Q401X": "q401x",     # Some regions split year/month; handled below
    "Q402":  "q402",
    "Q404D1":"q40331",    # Birthplace of first child (2015 child module D1)
}
df.rename(columns={k: v for k,v in rename_map_2015.items() if k in df.columns}, inplace=True)

# 2) Birth year-month: 2015 splits q101c1y + q101c1m → combine into q101c1 (e.g., 197807)
if {"q101c1y","q101c1m"} <= set(df.columns):
    y = pd.to_numeric(df["q101c1y"], errors="coerce").astype("Int64")
    m = pd.to_numeric(df["q101c1m"], errors="coerce").astype("Int64")
    df["q101c1"] = y.astype(str).str.replace("<NA>","") + m.astype(str).str.zfill(2).str.replace("<NA>","")
elif "a101c1" in df.columns:
    df.rename(columns={"a101c1":"q101c1"}, inplace=True)

# 3) Current migration time: if q101j1 is missing, combine q101k1y/q101k1m → q101j1
if "q101j1" not in df.columns and {"q101k1y","q101k1m"} <= set(df.columns):
    yy = pd.to_numeric(df["q101k1y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["q101k1m"], errors="coerce").astype("Int64")
    df["q101j1"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")

# 4) First marriage time: if split (Q305Y/M or Q401/401X), combine → q401
if {"Q305Y","Q305M"} <= set(df.columns) and "q401" not in df.columns:
    yy = pd.to_numeric(df["Q305Y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["Q305M"], errors="coerce").astype("Int64")
    df["q401"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")

# 5) Food/rent: if multiple columns (Q1021/Q1022 or rent_m2), merge into main column
if {"q102_1","q102_2"} <= set(df.columns):
    df["q102"] = pd.to_numeric(df["q102_1"], errors="coerce").fillna(0) + \
                 pd.to_numeric(df["q102_2"], errors="coerce").fillna(0)

# 6) Ensure key q101 columns exist (fill missing to avoid KeyError)
def _ensure(target, cands, fill=np.nan):
    if target in df.columns: return
    for c in cands:
        if c in df.columns:
            df[target] = df[c]; return
    df[target] = fill

_ensure("q101b1", ["q101b1","gender_1","Q101B"])
_ensure("q101e1", ["q101e1","resi_place_1","Q101E"])
_ensure("q101f1", ["q101f1","nation_1","Q101F"])
_ensure("q101g1", ["q101g1","edu_stat_1","edu_status_1","Q101G"])
_ensure("q101h1", ["q101h1","acc_nat_1","acc_nature_1","Q101H"])
_ensure("q101i1", ["q101i1","flo_rage_1","Q101I"])
_ensure("q101k2", ["q101k2","mar_status_2"])   # Sometimes provided as q101k2y/m, ensure column exists
_ensure("q101l2", ["q101l2","emp_status_2"], fill=np.nan)  # 2015 lacks spouse employment; handled later

# 7) City information (city_clean/is_beijing/is_shanghai): often in F3/F2 or city_40
city_cands = [c for c in ["city_40","F3","F2","pro","pro_name"] if c in df.columns]
if city_cands:
    cc = city_cands[0]
    df["city_clean"]  = df[cc].astype(str).str.strip()
    df["is_beijing"]  = df["city_clean"].str.contains("北京").astype(int)
    df["is_shanghai"] = df["city_clean"].str.contains("上海").astype(int)

# 8) Working hours columns (q208/q209): ensure existence to avoid KeyError
for c in ["q208","q209"]:
    if c not in df.columns: df[c] = np.nan

# 9) 2015 A-form usually lacks q5101~q5105 (happiness survey), create empty columns to avoid merge errors
for c in ["q5101","q5102","q5103","q5104","q5105"]:
    if c not in df.columns: df[c] = np.nan

# 10) Set base year for age/marriage duration calculations
df["__BASE_YEAR__"] = BASE_YEAR
# ===================== 2015 Adaptation Layer END =====================

# Food expenditure: merge if split into A/B columns
if "q102" not in df.columns:
    a = pd.to_numeric(df.get("foodcost_m"),  errors="coerce").fillna(0)
    b = pd.to_numeric(df.get("foodcost_m2"), errors="coerce").fillna(0)
    df["q102"] = a + b

# Remittance (money sent home): if not available, map from other variants
if "money_home" in df.columns:
    df["q104"] = pd.to_numeric(df["money_home"], errors="coerce")
elif "q510" in df.columns:
    df["q104"] = pd.to_numeric(df["q510"], errors="coerce")
else:
    df["q104"] = np.nan

rename_map = rename_map_2015
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# Merge food expenditure columns into q102 (A+B)
if "q102b" in df.columns:
    df["q102"] = pd.to_numeric(df.get("q102"), errors="coerce").fillna(0) + \
                 pd.to_numeric(df.get("q102b"), errors="coerce").fillna(0)

# Insurance (you later reference q502a..q502f; ensure columns exist)
for c in ["q502a","q502b","q502c","q502d","q502e","q502f"]:
    if c not in df.columns:
        df[c] = np.nan

# Apply mapping
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# === Merge food expenditure into q102 (A self-paid + B subsidized) ===
if "foodcost_m" in df.columns or "q102a" in df.columns:
    a = df.get("q102a", df.get("foodcost_m"))
    b = df.get("q102b", df.get("foodcost_m2"))
    a = pd.to_numeric(a, errors="coerce").fillna(0)
    b = pd.to_numeric(b, errors="coerce").fillna(0)
    df["q102"] = a + b
else:
    df["q102"] = np.nan

# Keep rent_m for derived calculations
if "q302_rent" in df.columns:
    df["rent_m"] = pd.to_numeric(df["q302_rent"], errors="coerce")

print("✅ Completed 2012→2011 field renaming and unification.")
