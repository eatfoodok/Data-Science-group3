# 🧹 Clean_code.py

## Overview
This script processes **China’s 2011 Individual Migration Dataset** (`2011年个人数据(STATA).dta`) and generates a cleaned dataset (`clean_2011.csv`).  
It automates data loading, transformation, dummy variable creation, winsorization, and feature engineering for migration, employment, and socioeconomic analysis.

## 📂 Input and Output
| File | Description |
|------|--------------|
| `2011年个人数据(STATA).dta` | Original STATA dataset containing individual-level migration and demographic information. |
| `clean_2011.csv` | Cleaned and transformed dataset ready for analysis. |

## ⚙️ Workflow Summary
1. **Data Loading**
   - Loads the STATA file automatically from the current script directory.
   - Converts categorical data to numeric format.

2. **City and Demographics**
   - Creates binary indicators (`is_beijing`, `is_shanghai`, `male`, `is_han`).
   - Extracts and cleans age from birth year, handling outliers and invalid entries.

3. **Education Classification**
   - Converts raw education codes (`q101g1`) into four education-level dummies:
     - `high_school`, `junior_college`, `bachelor`, `graduate`.
   - Ensures mutual exclusivity (only one level active per individual).

4. **Migration Variables**
   - Creates multiple migration indicators:
     - `Migrate`: migrated or not.
     - `Migrate_1`: inter-provincial.
     - `Migrate_2`: intra-provincial.
     - `Migrate_3`: intra-city.
   - Calculates years since migration (`migration_interval`).

5. **Marriage and Employment**
   - Generates `marriage`, `employed`, and employment-type classifications (`formal`, `informal`, `self_employed`) based on occupation codes.
   - Calculates weekly working hours.

6. **Income and Expenditure Cleaning**
   - Processes monetary variables (income, expenditure, rent, remittance).
   - Applies **95% winsorization** to handle outliers and missing values.
   - Generates new columns with `_win` suffix (e.g., `income_total_m_win`).

7. **Family and Children**
   - Calculates `length_marriage`, `kids_number`, and whether children were born locally (`birth_here`).

8. **Social Security and Welfare**
   - Constructs binary coverage flags for:
     - Pension, Medical, Work, Unemployment, Maternity, and Housing Fund insurance.

9. **Subjective Happiness Index**
   - Combines five survey questions (`q5101–q5105`) into a composite happiness score (0–17).

10. **Export**
    - Saves final cleaned dataset as UTF-8 encoded CSV file `clean_2011.csv`.

## 🧩 Key Functions
### `winsorize_95(series)`
Truncates numeric values above the 95th percentile and replaces missing values with 0.  
Used for cleaning income, expenditure, and rent data.

### `classify_employment(row)`
Maps raw occupational codes into simplified employment categories.

## 🧠 Main Outputs
| Variable | Description |
|-----------|--------------|
| `age` | Age computed from birth year |
| `male`, `is_han` | Gender and ethnicity dummies |
| `high_school`, `bachelor`, etc. | Education levels |
| `Migrate`, `Migrate_1`, ... | Migration status indicators |
| `employment_group` | Employment type (formal/informal/self-employed) |
| `income_total_m_win`, etc. | Winsorized financial variables |
| `Happiness` | Composite happiness score |
| `Pension_Insurance`, ... | Welfare coverage flags |

## 🧰 Requirements
- **Python 3.8+**
- **Libraries**
  ```bash
  pip install pandas numpy
  ```

## 🧾 Notes
- Invalid or extreme numeric values are replaced or clipped to improve robustness.
- The script assumes **2011** as the base year for calculating ages and durations.
- Output file is saved automatically in the same directory as the script.

## 💡 Usage
```bash
python Clean_code.py
```

After execution, you’ll see:
```
✔ 已加载 2011年个人数据(STATA).dta
✔ 已保存到: clean_2011.csv
```
