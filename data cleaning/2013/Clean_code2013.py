# ==== 1) Basic Libraries ====
import os  # Handle file paths
import re  # Regular expressions, used for field name recognition
import json  # Save field matching logs
import numpy as np  # Numerical computation
import pandas as pd  # Main library for data processing
from datetime import datetime  # Handle date operations
from textwrap import dedent  

# ===== 2013 Simplified Reading =====
import pandas as pd
import os

# Get current script directory
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "2013年个人数据.dta")

# Read file
df = pd.read_stata(file_path, convert_categoricals=False)
print(f"✔ Loaded {file_path}")
# =====================
BASE_YEAR = 2013

import numpy as np
import pandas as pd

# 1) Rename columns to match your 2011 code naming convention
rename_map = {
    "gender_1":     "q101b1",
    "resi_place_1": "q101e1",
    "nation_1":     "q101f1",
    "edu_status_1": "q101g1",
    "acc_nature_1": "q101h1",
    "cur_place_1":  "q101j1_place",    # Placeholder, not used later
    "flo_rage_1":   "q101i1",
    "floyear_1":    "q101j1_y",
    "flomon_1":     "q101j1_m",

    "mar_status_2": "q101k2",          # Spouse marriage
    # 2013 has no emp_status_2; q101l2 will be added later

    "unit_quality": "q204",
    "emly_ident":   "q207",
    "aver_days":    "q208",
    "aver_hours":   "q209",

    "foodcost_m":   "q102",
    "cost_m":       "q103",
    "famincom_m":   "q105",
    "rent_m":       "q302",            # Used as rent column later

    "firmarr_y":    "q401_y",
    "firmarr_m":    "q401_m",
    "fer_numb":     "q402",
    "bir_place_1":  "q40331",

    "love_city":       "q5101",
    "atte_change":     "q5102",
    "loca_integrate":  "q5103",
    "loca_accept":     "q5104",
    "loca_despise":    "q5105",
    
}
df.rename(columns={k: v for k,v in rename_map.items() if k in df.columns}, inplace=True)

# 2) Combine birth year and month into q101c1 (birt_y_1 + birt_m_1)
if {"birt_y_1","birt_m_1"} <= set(df.columns):
    y = pd.to_numeric(df["birt_y_1"], errors="coerce").astype("Int64")
    m = pd.to_numeric(df["birt_m_1"], errors="coerce").astype("Int64")
    df["q101c1"] = y.astype(str).str.replace("<NA>","") + m.astype(str).str.zfill(2).str.replace("<NA>","")
elif "a101c1" in df.columns:
    df.rename(columns={"a101c1":"q101c1"}, inplace=True)
elif "q101c1" not in df.columns:
    raise KeyError("Missing birth date columns (birt_y_1/birt_m_1/a101c1) in 2013 dataset")

# 3) Combine migration year/month into q101j1 (q101j1_y + q101j1_m)
if {"q101j1_y","q101j1_m"} <= set(df.columns):
    yy = pd.to_numeric(df["q101j1_y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["q101j1_m"], errors="coerce").astype("Int64")
    df["q101j1"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")
else:
    # If missing, create empty column to avoid slicing errors later
    df["q101j1"] = np.nan

# 4) Combine first marriage year/month into q401 (q401_y + q401_m)
if {"q401_y","q401_m"} <= set(df.columns):
    yy = pd.to_numeric(df["q401_y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["q401_m"], errors="coerce").astype("Int64")
    df["q401"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")
else:
    df["q401"] = np.nan

# 5) Convert text fields to expected numeric encoding
# Ethnicity: your original code uses (q101f1==1); 2013 uses text "Han"
df["q101f1"] = df["q101f1"].astype(str)
# Education: 2013 uses Chinese strings, convert to 1–8 scale
edu_map = {"未上过学":1,"小学":2,"初中":3,"高中":4,"中专":5,"大学专科":6,"大专":6,"大学本科":7,"本科":7,"研究生":8}
df["q101g1"] = pd.to_numeric(df["q101g1"].map(edu_map), errors="coerce").fillna(pd.to_numeric(df["q101g1"], errors="coerce"))

# Hukou type: 2013 may have text or garbled strings (e.g., “ũҵ”); check for “农”/“非”
q_h1 = df["q101h1"].astype(str)
df["q101h1"] = np.where(q_h1.str.contains("农"), 1,
                 np.where(q_h1.str.contains("非"), 2, pd.to_numeric(q_h1, errors="coerce")))

# 6) 2013 lacks spouse employment column; add q101l2 with fallback based on emly_ident
if "q101l2" not in df.columns:
    # Roughly infer “employed” if contains employment-related words
    eid = df.get("q207").astype(str)
    df["q101l2"] = np.where(eid.str.contains("雇|自营|雇主|帮工|员|主"), 1, 0)

# 7) Insurance fields: your later code directly references q502a..q502f; create if missing
for c in ["q502a","q502b","q502c","q502d","q502e","q502f"]:
    if c not in df.columns:
        df[c] = np.nan

# 8) Set base year to 2013 (so age/marriage/migration calculations use this year)
df["__BASE_YEAR__"] = BASE_YEAR

# ===== Combine “year + month” fields for compatibility =====
# Birthdate: birt_y_1 + birt_m_1 → q101c1 (e.g., 196711)
if {"birt_y_1","birt_m_1"} <= set(df.columns):
    y = pd.to_numeric(df["birt_y_1"], errors="coerce").astype("Int64")
    m = pd.to_numeric(df["birt_m_1"], errors="coerce").astype("Int64")
    df["q101c1"] = y.astype(str).str.replace("<NA>","") + m.astype(str).str.zfill(2).str.replace("<NA>","")
elif "a101c1" in df.columns:  # Rare variant
    df.rename(columns={"a101c1":"q101c1"}, inplace=True)
else:
    # Leave as-is; later logic will handle missing age
    pass

# Migration year-month: q101j1_y + q101j1_m → q101j1
if {"q101j1_y","q101j1_m"} <= set(df.columns):
    yy = pd.to_numeric(df["q101j1_y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["q101j1_m"], errors="coerce").astype("Int64")
    df["q101j1"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")

# First marriage year-month: q401_y + q401_m → q401
if {"q401_y","q401_m"} <= set(df.columns):
    yy = pd.to_numeric(df["q401_y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["q401_m"], errors="coerce").astype("Int64")
    df["q401"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")

# ===== Merge A/B columns for food/rent while keeping original variable names =====
if "q102b" in df.columns:
    df["q102"] = pd.to_numeric(df["q102"], errors="coerce").fillna(0) + \
                 pd.to_numeric(df["q102b"], errors="coerce").fillna(0)
if "q302b" in df.columns:
    df["q302"] = pd.to_numeric(df["q302"], errors="coerce").fillna(0) + \
                 pd.to_numeric(df["q302b"], errors="coerce").fillna(0)

# ===== 2014 dataset lacks spouse employment (q101l2); provide robust fallback =====
if "q101l2" not in df.columns:
    eid_raw = df.get("q207")
    eid = (eid_raw.astype(str)
           if isinstance(eid_raw, pd.Series)
           else pd.Series("", index=df.index))
    df["q101l2"] = np.where(eid.str.contains("雇|自营|雇主|帮工|员|主"), 1, 0)

# ===== City column setup for city_clean / is_beijing / is_shanghai =====
city_col = "city_name" if "city_name" in df.columns else ("pro_name" if "pro_name" in df.columns else None)
if city_col:
    df["city_clean"] = df[city_col].astype(str).str.strip()
    df["is_beijing"]  = df["city_clean"].str.contains("北京").astype(int)
    df["is_shanghai"] = df["city_clean"].str.contains("上海").astype(int)
