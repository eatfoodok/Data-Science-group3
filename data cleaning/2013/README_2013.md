# 🧹 Clean_code2013.py

## Overview
This script cleans and standardizes the **2013 Individual Migration Dataset** (`2013年个人数据.dta`) to match the 2011 baseline format.  
It unifies variable names, converts textual responses into numeric codes, constructs derived variables, handles missing data, and produces a cleaned dataset ready for empirical analysis.

## 📂 Input and Output
| File | Description |
|------|--------------|
| `2013年个人数据.dta` | Raw STATA dataset with demographic, employment, and migration details. |
| `clean_2013.csv` | Cleaned and standardized dataset exported as UTF-8 CSV. |

## ⚙️ Workflow Summary

1. **File Loading and Preparation**
   - Automatically locates and loads `2013年个人数据.dta` from the same directory.
   - Defines `BASE_YEAR = 2013` for age and duration calculations.

2. **Variable Renaming and Alignment**
   - Renames 2013 variables to the 2011 naming scheme (e.g., `gender_1 → q101b1`, `edu_status_1 → q101g1`).
   - Merges year-month pairs (e.g., `birt_y_1` + `birt_m_1` → `q101c1`) for consistent date handling.
   - Ensures compatibility across all core demographic and employment fields.

3. **Data Normalization**
   - Converts Chinese text responses (e.g., “汉”, “未上过学”) into numeric categories for ethnicity and education.
   - Maps text in `q101h1` (agricultural / non-agricultural hukou) to standard numeric values.

4. **Derived Fields Construction**
   - Creates unified columns:
     - `q101c1`: birth year and month
     - `q101j1`: migration year and month
     - `q401`: first marriage year and month
   - Combines food expenditure (`q102`, `q102b`) and rent fields (`q302`, `q302b`).

5. **Dummy and Indicator Variables**
   - `is_beijing` / `is_shanghai` from `city_clean`.
   - `male` dummy from `q101b1`.
   - `is_han` dummy from ethnicity field.
   - `rural` dummy for agricultural hukou.

6. **Education Classification**
   - Converts `q101g1` into four dummies: `high_school`, `junior_college`, `bachelor`, `graduate`.
   - Enforces mutual exclusivity between levels.

7. **Migration Indicators**
   - `Migrate`, `Migrate_1`, `Migrate_2`, `Migrate_3` — representing overall and hierarchical migration types.
   - `migration_interval` = `BASE_YEAR` − migration year.

8. **Marriage and Employment**
   - `marriage` and `employed` from corresponding codes.
   - Missing `q101l2` filled using text-based employment inference.
   - Classifies jobs into categories (`formal`, `informal`, `self_employed`) using `classify_employment()`.

9. **Income, Expenditure, and Winsorization**
   - Processes financial variables:
     - `income_total_m`, `exp_total_m`, `food_exp_m`, `income_to_home`, `rent_m`.
   - Applies **95% winsorization** and fills missing values with zero.
   - Creates `_win`-suffixed columns for cleaned numeric versions.

10. **Work Hours and Stress Indicators**
    - Standardizes workday (`q208`) and workhour (`q209`) columns.
    - Computes `hours_per_week` and `hours_per_week_filled`.

11. **Family and Marriage Duration**
    - Calculates `length_marriage`, `kids_number`, and `birth_here` for children’s local birthplace.

12. **Social Welfare Coverage**
    - Constructs six flags: `Pension_Insurance`, `Medical_Insurance`, `Work_Insurance`, `Unemploy_Insurance`, `Maternity_Insurance`, `Housing_Fund`.

13. **Happiness Index**
    - Maps Likert-scale responses (1–4 or text equivalents) and computes:
      ```
      Happiness = q5101 + q5102 + q5103 + q5104 - q5105
      ```
    - Higher scores indicate greater subjective well-being.

14. **Export**
    - Outputs cleaned dataset as `clean_2013.csv` encoded in UTF-8.

## 🧩 Key Functions

### `winsorize_95(series)`
Applies a 95th percentile cutoff to remove extreme outliers and replaces missing values with 0.

### `classify_employment(row)`
Groups occupation and employment identity codes into standardized employment categories.

### `_ensure_col(df, target, cands)`
Ensures expected column names exist by checking multiple candidates and creating fallback variables.

## 🧠 Main Outputs
| Variable | Description |
|-----------|--------------|
| `age` | Age derived from birth year |
| `male`, `is_han`, `rural` | Basic demographic dummies |
| `high_school`, `bachelor`, etc. | Education levels |
| `Migrate`, `Migrate_1`, ... | Migration indicators |
| `employment_group` | Employment classification |
| `income_total_m_win`, etc. | Winsorized financial data |
| `hours_per_week` | Total weekly work hours |
| `Happiness` | Composite subjective well-being score |

## 🧰 Requirements
- **Python 3.8+**
- **Libraries**
  ```bash
  pip install pandas numpy
  ```

## 🧾 Notes
- All Chinese text responses are automatically converted to numeric values.
- Outlier handling and missing-value imputation ensure analytical consistency.
- The final cleaned CSV is saved in the same directory as the script.

## 💡 Usage
```bash
python Clean_code2013.py
```

Expected output:
```
✔ 已加载 2013年个人数据.dta
✅ Variables unified and renamed successfully.
✔ Saved to: clean_2013.csv
```
