# derive_map.ipynb

This notebook is used to **generate standardized variable mappings** for different survey datasets (e.g., 2011–2017).  
It reads a base Excel mapping file and produces a unified JSON dictionary that standardizes variable names across years.

---

## 📘 Purpose
Different survey years often use inconsistent column names (for example, `Q105` vs. `q105`).  
This notebook creates a **mapping dictionary** that aligns all variable names to a consistent schema.

---

## ⚙️ Workflow
1. **Input File**
   - `mapping_base.xlsx`  
     Must include two columns:
     - `original`: Original variable names from raw datasets  
     - `standardized`: Unified variable names you want to use

2. **Execution Steps**
   - Reads the Excel file into a pandas DataFrame  
   - Builds a Python dictionary with key-value pairs  
   - Exports the mapping as `derived_map.json`

3. **Output File**
   - `derived_map.json`  
     A UTF-8 encoded JSON file storing all standardized variable name mappings.

---

## 🧠 Example
```python
import json

with open('derived_map.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

print(mapping['Q105'])
# → 'q105'
```

---

## 🧾 Requirements
- Python ≥ 3.8  
- Libraries: `pandas`, `json`, `openpyxl`

Install dependencies:
```bash
pip install pandas openpyxl
```

---

## 💡 Notes
- Keep your Excel file clean (no empty rows).
- You can extend this notebook for automatic mapping validation across yearly datasets.
