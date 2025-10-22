# 🧹 Clean_code.py (2012 Version)

## Overview
This script cleans and standardizes the **2012 Individual Migration Dataset** (`2012年 个人数据 【全】.dta`) to match the 2011 data structure.  
It harmonizes field names, creates dummy variables, handles missing values, and exports a cleaned dataset (`clean_2012.csv`) for subsequent analysis.

## 📂 Input and Output
| File | Description |
|------|--------------|
| `2012年 个人数据 【全】.dta` | Original STATA dataset with individual-level demographic, employment, and migration data. |
| `clean_2012.csv` | Cleaned and standardized dataset ready for analysis. |

## ⚙️ Workflow Summary
1. **File Loading and Variable Mapping**
   - Automatically locates and loads the `.dta` file from the same directory.
   - Renames 2012 variable names to align with 2011 equivalents (e.g., `gender_1 → q101b1`, `birt_date_1 → q101c1`, etc.).
   - Combines split food expenditure variables (`q102a`, `q102b`) into a unified column `q102`.

2. **Basic Demographics**
   - Creates binary flags for Beijing and Shanghai.
   - Generates gender (`male`), age (from birth year), and ethnicity (`is_han`).
   - Handles abnormal ages (<0 or >120) by marking them as missing.

3. **Education and Household Registration**
   - Converts `q101g1` into four education-level dummy variables:
     - `high_school`, `junior_college`, `bachelor`, `graduate`.
   - Ensures mutual exclusivity across education levels.
   - Creates `rural` dummy (1 = agricultural household).

4. **Migration Features**
   - Constructs migration status indicators:
     - `Migrate`, `Migrate_1`, `Migrate_2`, `Migrate_3`.
   - Calculates years since migration (`migration_interval`).

5. **Marriage and Employment**
   - Adds marital status (`marriage`) and employment dummy (`employed`).
   - Classifies jobs into categories:
     - `public_sector`, `private_enterprise`, `self_employed`, `employer`, `family_worker`, `casual_worker`, `other`.
   - Groups them into broader categories: `formal`, `informal`, and `self_employed`.
   - Calculates total weekly working hours.

6. **Income and Expenditure Cleaning**
   - Processes key monetary variables:
     - Monthly income, total expenditure, food expenditure, remittance, rent.
   - Applies 95% winsorization to remove outliers and replaces missing values with 0.
   - Creates `_win`-suffixed variables for cleaned values (e.g., `income_total_m_win`).

7. **Family, Children, and Marriage Duration**
   - Calculates years since marriage (`length_marriage`), number of children (`kids_number`), and local birth indicator (`birth_here`).

8. **Social Insurance and Welfare**
   - Constructs six welfare coverage flags:
     - `Pension_Insurance`, `Medical_Insurance`, `Work_Insurance`, `Unemploy_Insurance`, `Maternity_Insurance`, `Housing_Fund`.

9. **Subjective Happiness Index**
   - Computes composite happiness score:
     ```
     Happiness = q5101 + q5102 + q5103 + q5104 - q5105
     ```

10. **Export**
    - Outputs cleaned dataset as UTF-8 encoded `clean_2012.csv`.

## 🧩 Key Functions
### `winsorize_95(series)`
Truncates values above the 95th percentile and replaces missing values with 0.  
Used for financial variables to handle outliers.

### `classify_employment(row)`
Maps raw employment-related fields into standardized categories used in employment analysis.

## 🧠 Main Outputs
| Variable | Description |
|-----------|--------------|
| `age` | Age derived from birth year |
| `male`, `is_han` | Gender and ethnicity |
| `high_school`, `bachelor`, etc. | Education level flags |
| `Migrate`, `Migrate_1`, ... | Migration indicators |
| `employment_group` | Employment group classification |
| `income_total_m_win`, ... | Winsorized income/expenditure variables |
| `Happiness` | Composite subjective happiness score |
| `Pension_Insurance`, ... | Social welfare coverage flags |

## 🧰 Requirements
- **Python 3.8+**
- **Libraries**
  ```bash
  pip install pandas numpy
  ```

## 🧾 Notes
- Automatically handles renaming inconsistencies between 2011 and 2012 datasets.
- 2011 is used as the reference year for age and duration calculations.
- The final output is saved in the same directory as the script.

## 💡 Usage
```bash
python Clean_code.py
```

After running successfully:
```
✔ 已加载 2012年 个人数据 【全】.dta
✅ 已完成 2012→2011 字段名重命名，统一完成。
✔ 已保存到: clean_2012.csv
```
