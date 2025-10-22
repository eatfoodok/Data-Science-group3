# 🧹 Clean_code2014.py

## Overview
This script processes and standardizes the **2014 China Individual Migration Survey (A Volume)** (`2014年全国个人A卷.dta`) to match the structure and variable definitions of the 2011 baseline dataset.  
It harmonizes column names, converts categorical values, generates derived fields, applies winsorization, and outputs a clean dataset `clean_2014.csv` for econometric or demographic analysis.

## 📂 Input and Output
| File | Description |
|------|--------------|
| `2014年全国个人A卷.dta` | Original STATA dataset containing personal-level demographic, employment, and household data. |
| `clean_2014.csv` | Cleaned and standardized CSV file ready for downstream analysis. |

## ⚙️ Workflow Summary

1. **File Loading**
   - Automatically locates and reads the `.dta` source file.
   - Prints confirmation once loaded successfully.

2. **Variable Standardization (2014 → 2011 Format)**
   - Renames 2014 variables to match 2011 naming conventions:
     - Example: `gender_1 → q101b1`, `edu_stat_1 → q101g1`, `flo_rage_1 → q101i1`, `famincom_m → q105`.
   - Handles missing or differently named columns (e.g., birth date, marriage date, rent, and food expenditure).

3. **Combined Date Variables**
   - Constructs year+month composite fields:
     - `birt_y_1 + birt_m_1 → q101c1` (birth date)
     - `q101j1_y + q101j1_m → q101j1` (migration date)
     - `q401_y + q401_m → q401` (first marriage date)

4. **Expense and Income Merging**
   - Merges duplicate food and rent expenditure columns (e.g., `q102a + q102b → q102`).
   - Ensures consistent numeric formatting and fills missing values.

5. **Employment Handling**
   - Since 2014 lacks a spouse employment field (`q101l2`), the script infers employment from text in `q207` (e.g., words like “employer”, “self-employed”, “worker”).

6. **City-Level Indicators**
   - Extracts and cleans city names into `city_clean`.
   - Generates `is_beijing` and `is_shanghai` binary indicators.

7. **Demographics and Core Variables**
   - Constructs gender (`male`), age (from `q101c1`), and ethnicity (`is_han`).
   - Removes outliers in age (<0 or >120).

8. **Education Classification**
   - Converts `q101g1` to four mutually exclusive dummy variables:
     - `high_school`, `junior_college`, `bachelor`, `graduate`.

9. **Migration Status**
   - Builds multiple migration indicators:
     - `Migrate` (any migration), `Migrate_1` (inter-provincial), `Migrate_2` (inter-city), `Migrate_3` (intra-county).
   - Calculates `migration_interval` = 2011 − migration year.

10. **Marriage and Employment Dummies**
    - Generates `marriage` (1 = married) and `employed` (1 = working).
    - Handles missing or inconsistent values.

11. **Income and Expenditure Processing**
    - Normalizes financial variables: total income, total expenditure, food expense, remittance, rent.
    - Applies **95% winsorization** to control outliers and fills missing values with 0.
    - Creates `_win`-suffixed columns (e.g., `income_total_m_win`).

12. **Employment Classification**
    - Categorizes employment into formal, informal, and self-employed groups using a rule-based mapping via `classify_employment()`.

13. **Working Hours**
    - Ensures availability of `q208` (days/week) and `q209` (hours/day).
    - Computes total weekly work hours (`hours_per_week`).

14. **Family and Marriage Duration**
    - Derives number of children (`kids_number`), years since marriage (`length_marriage`), and child birthplace (`birth_here`).

15. **Social Insurance and Benefits**
    - Constructs six binary indicators for social security coverage:
      - `Pension_Insurance`, `Medical_Insurance`, `Work_Insurance`, `Unemploy_Insurance`, `Maternity_Insurance`, `Housing_Fund`.

16. **Subjective Happiness Index**
    - Converts Likert-scale responses (1–4) to numeric.
    - Computes composite happiness score:
      ```
      Happiness = q5101 + q5102 + q5103 + q5104 - q5105
      ```
    - Higher scores represent higher subjective well-being.

17. **Output**
    - Saves final cleaned data as `clean_2014.csv` (UTF-8 encoding).

## 🧩 Key Functions

### `winsorize_95(series)`
Truncates extreme values above the 95th percentile and replaces missing values with zero.

### `classify_employment(row)`
Categorizes employment type based on `q204` (sector) and `q207` (employment identity).

### `_ensure_col(df, target, cands)`
Automatically creates required columns (e.g., workdays/hours) by checking multiple name variants.

## 🧠 Main Outputs
| Variable | Description |
|-----------|--------------|
| `age` | Age calculated from birth year |
| `male`, `is_han`, `rural` | Demographic dummies |
| `high_school`, `bachelor`, etc. | Education level indicators |
| `Migrate`, `Migrate_1`, ... | Migration status |
| `employment_group` | Employment group (formal, informal, self-employed) |
| `income_total_m_win` | Winsorized monthly income |
| `hours_per_week` | Total weekly working hours |
| `Happiness` | Composite happiness index |

## 🧰 Requirements
- **Python 3.8+**
- **Libraries**
  ```bash
  pip install pandas numpy
  ```

## 🧾 Notes
- The script assumes 2011 as the reference year for time-based calculations.
- Missing and inconsistent variables are handled gracefully using fallbacks.
- All Chinese categorical values are converted to numeric for consistency.

## 💡 Usage
```bash
python Clean_code2014.py
```

Expected console output:
```
✔ 已加载 2014年全国个人A卷.dta
✅ Variable alignment complete.
✔ Saved to: clean_2014.csv
```
