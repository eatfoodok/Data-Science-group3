# merge_data.ipynb

This notebook combines multiple **yearly cleaned survey datasets** into one unified CSV file.  
It assumes each year’s dataset has already been standardized (e.g., variable names matched via `derive_map.ipynb`).

---

## 📘 Purpose
After data cleaning, each year (e.g., `clean_2011.csv`, `clean_2012.csv`) exists as a separate file.  
This script merges all of them into a single **panel dataset** for longitudinal analysis.

---

## ⚙️ Workflow
1. **Input Folder**
   - Directory: `data/cleaned/`  
     Contains files named like:
     ```
     clean_2011.csv
     clean_2012.csv
     clean_2013.csv
     ...
     ```

2. **Execution Steps**
   - Scans for all files matching pattern `clean_20*.csv`
   - Reads each CSV into a pandas DataFrame
   - Concatenates them into one DataFrame (`pd.concat`)
   - Exports final merged dataset as `merged_clean.csv`

3. **Output File**
   - `merged_clean.csv`  
     Combined dataset containing all years.

---

## 🧠 Example
```python
import pandas as pd

df = pd.read_csv('merged_clean.csv')
print(df.shape)
# (rows, columns)
```

---

## 🧾 Requirements
- Python ≥ 3.8  
- Libraries: `pandas`, `glob`

Install dependencies:
```bash
pip install pandas
```

---

## 💡 Notes
- Ensure all yearly CSVs have identical column structures before merging.
- Adjust file path (`base = 'data/cleaned'`) if your folder structure differs.
- The merged file uses UTF-8-SIG encoding to preserve Chinese characters.
