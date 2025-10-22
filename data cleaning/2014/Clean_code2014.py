# ==== 1) Basic Libraries ====
import os  # Handle file paths
import re  # Regular expressions, used for field name recognition
import json  # Save field matching logs
import numpy as np  # Numerical computation
import pandas as pd  # Main library for data processing
from datetime import datetime  # Handle date operations
from textwrap import dedent  # Format text neatly

# ===== 2014 Simplified Reading =====
import pandas as pd
import os

# Get current script directory
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "2014年全国个人A卷.dta")

# Read file
df = pd.read_stata(file_path, convert_categoricals=False)
print(f"✔ Loaded {file_path}")
# ================= 2014 → 2011 Format: Unified Renaming =================
rename_map = {
    # 101 (Person 1 = respondent)
    "gender_1":     "q101b1",
    "resi_place_1": "q101e1",      # Hukou location
    "nation_1":     "q101f1",      # Ethnicity
    "edu_stat_1":   "q101g1",      # Education (note 2014 uses edu_stat_1)
    "acc_nat_1":    "q101h1",      # Hukou type (2014: acc_nat_1)
    "cur_place_1":  "q101j1_place",
    "flo_rage_1":   "q101i1",      # Migration range 1/2/3
    "floyear_1":    "q101j1_y",    # Year of migration
    "flomon_1":     "q101j1_m",    # Month of migration

    # Spouse (Person 2) marital status; 2014 has no emp_status_2, needs fallback
    "mar_status_2": "q101k2",

    # Employment/industry/organization type/identity (classification uses q204, q207; add q203 for industry)
    "job_indu":     "q203",
    "unit_quality": "q204",
    "emly_iden":    "q207",

    # Income/expenditure (2014: questions 215/216/217/218)
    "foodcost_m":   "q102",        # Household monthly food expenditure (2014 Q215)
    "foodcost_m2":  "q102b",       # If second column exists, merge into q102
    "rent_m":       "q302",        # Rent (2014 Q216; your code uses q302 as rent)
    "rent_m2":      "q302b",       # If second column exists, merge into rent_m
    "cost_m":       "q103",        # Household total monthly expenditure (2014 Q217)
    "famincom_m":   "q105",        # Household total monthly income (2014 Q218)

    # Marriage & fertility (first marriage/year/child number/first child birthplace)
    "firmarr_y":    "q401_y",
    "firmarr_m":    "q401_m",
    "fer_numb":     "q402",
    "bir_place_1":  "q40331",
}
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# ===== Combine “year + month” into single columns for legacy compatibility =====
# Birthdate: birt_y_1 + birt_m_1 → q101c1 (e.g., 196711)
if {"birt_y_1","birt_m_1"} <= set(df.columns):
    y = pd.to_numeric(df["birt_y_1"], errors="coerce").astype("Int64")
    m = pd.to_numeric(df["birt_m_1"], errors="coerce").astype("Int64")
    df["q101c1"] = y.astype(str).str.replace("<NA>","") + m.astype(str).str.zfill(2).str.replace("<NA>","")
elif "a101c1" in df.columns:  # Rare variant
    df.rename(columns={"a101c1":"q101c1"}, inplace=True)
else:
    # If missing, let later age logic handle it
    pass

# Migration year/month: q101j1_y + q101j1_m → q101j1
if {"q101j1_y","q101j1_m"} <= set(df.columns):
    yy = pd.to_numeric(df["q101j1_y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["q101j1_m"], errors="coerce").astype("Int64")
    df["q101j1"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")

# First marriage year/month: q401_y + q401_m → q401
if {"q401_y","q401_m"} <= set(df.columns):
    yy = pd.to_numeric(df["q401_y"], errors="coerce").astype("Int64")
    mm = pd.to_numeric(df["q401_m"], errors="coerce").astype("Int64")
    df["q401"] = yy.astype(str).str.replace("<NA>","") + mm.astype(str).str.zfill(2).str.replace("<NA>","")

# ===== Merge A/B columns for food/rent while keeping old variable names =====
if "q102b" in df.columns:
    df["q102"] = pd.to_numeric(df["q102"], errors="coerce").fillna(0) + \
                 pd.to_numeric(df["q102b"], errors="coerce").fillna(0)
if "q302b" in df.columns:
    df["q302"] = pd.to_numeric(df["q302"], errors="coerce").fillna(0) + \
                 pd.to_numeric(df["q302b"], errors="coerce").fillna(0)

# ===== 2014 has no spouse employment (q101l2); provide fallback =====
if "q101l2" not in df.columns:
    # Roughly infer “employed”: contains keywords like “employer/self-employed/helper/staff”
    eid_raw = df.get("q207")
    eid = (eid_raw.astype(str)
           if isinstance(eid_raw, pd.Series)
           else pd.Series("", index=df.index))

    df["q101l2"] = np.where(eid.str.contains("雇|自营|雇主|帮工|员|主"), 1, 0)

# ===== City column setup for city_clean/is_beijing/is_shanghai =====
city_col = "city_name" if "city_name" in df.columns else ("pro_name" if "pro_name" in df.columns else None)
if city_col:
    df["city_clean"] = df[city_col].astype(str).str.strip()
    df["is_beijing"]  = df["city_clean"].str.contains("北京").astype(int)
    df["is_shanghai"] = df["city_clean"].str.contains("上海").astype(int)

# Food expenditure: 2013 had a single column (Q215), merge if split into A/B
if "q102" not in df.columns:
    a = pd.to_numeric(df.get("foodcost_m"),  errors="coerce").fillna(0)
    b = pd.to_numeric(df.get("foodcost_m2"), errors="coerce").fillna(0)  # Usually missing in 2013
    df["q102"] = a + b

# Remittance (money sent home): not present in 2013 A form; if C form or column 510 exists, map to q104
if "money_home" in df.columns:            # Some 2013 packages retain this column
    df["q104"] = pd.to_numeric(df["money_home"], errors="coerce")
elif "q510" in df.columns:                # Occasional variant
    df["q104"] = pd.to_numeric(df["q510"], errors="coerce")
else:
    df["q104"] = np.nan

# Ensure renaming execution
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# Merge food expenditure into q102 (A+B)
if "q102b" in df.columns:
    df["q102"] = pd.to_numeric(df.get("q102"), errors="coerce").fillna(0) + \
                 pd.to_numeric(df.get("q102b"), errors="coerce").fillna(0)

# Insurance fields (you later reference q502a..q502f; ensure existence)
for c in ["q502a","q502b","q502c","q502d","q502e","q502f"]:
    if c not in df.columns:
        df[c] = np.nan

# Execute renaming
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

# Keep rent_m column for later derived calculations
if "q302_rent" in df.columns:
    df["rent_m"] = pd.to_numeric(df["q302_rent"], errors="coerce")

print("✅ Completed 2012→2011 field renaming and unification.")
