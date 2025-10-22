# 🧹 clean_2015_with_hs.csv.py

## Overview
This script merges the **2015 China Individual Migration Survey (A Volume)** dataset (`a卷(STATA).dta`) with a pre-cleaned dataset (`clean_2015.csv`) to produce a final combined file `clean_2015_with_hs.csv`.  
Its primary purpose is to append the `q101h1` (household registration / hukou type) field from the raw STATA data into the cleaned dataset.

## 📂 Input and Output
| File | Description |
|------|--------------|
| `a卷(STATA).dta` | Original STATA dataset containing all survey variables. |
| `clean_2015.csv` | Cleaned version of the 2015 dataset without hukou information. |
| `clean_2015_with_hs.csv` | Final merged dataset including the additional hukou variable (`hs_residence_code`). |

## ⚙️ Workflow Summary

1. **Load Datasets**
   - Reads the raw STATA file (`a卷(STATA).dta`) with all survey variables.
   - Reads the pre-cleaned CSV (`clean_2015.csv`) that contains demographic and economic indicators.

2. **Select Relevant Variable**
   - Extracts only two columns from the STATA dataset:
     - `ID`: unique respondent identifier.
     - `q101h1`: hukou (household registration) code.

3. **Rename Columns**
   - Renames `q101h1` → `hs_residence_code` for clarity and consistency.

4. **Merge Datasets**
   - Performs a **left join** on the key column `ID`, ensuring all entries from the cleaned dataset remain intact.
   - Appends the new column `hs_residence_code` where available.

5. **Export Final Dataset**
   - Saves the merged dataset as `clean_2015_with_hs.csv` in UTF-8 encoding.
   - Prints a confirmation message when the process is complete.

## 🧠 Main Outputs
| Column | Description |
|---------|--------------|
| `ID` | Unique respondent identifier. |
| All variables from `clean_2015.csv` | Existing demographic, economic, and migration indicators. |
| `hs_residence_code` | Hukou type code extracted from `q101h1` in the STATA source. |

## 🧰 Requirements
- **Python 3.8+**
- **Libraries**
  ```bash
  pip install pandas
  ```

## 🧾 Notes
- The merge uses `how="left"` to preserve all records from the cleaned dataset.
- Any missing `hs_residence_code` values indicate the respondent’s ID did not exist in the STATA source file.
- Output encoding is UTF-8 with BOM (`utf-8-sig`) to ensure Excel compatibility.

## 💡 Usage
```bash
python clean_2015_with_hs.csv.py
```

Expected console output:
```
✔ 已匹配并保存 clean_2015_with_hs.csv
```
