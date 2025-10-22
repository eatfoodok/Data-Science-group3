import pandas as pd, os

base = os.path.dirname(__file__)
stata_path = os.path.join(base, "a卷(STATA).dta")
clean_path = os.path.join(base, "clean_2015.csv")

stata_df = pd.read_stata(stata_path, convert_categoricals=False)
clean_df = pd.read_csv(clean_path, encoding="utf-8-sig")

stata_sub = stata_df[["ID", "q101h1"]].rename(columns={"q101h1": "hs_residence_code"})
merged = clean_df.merge(stata_sub, on="ID", how="left")

merged.to_csv(os.path.join(base, "clean_2015_with_hs.csv"), index=False, encoding="utf-8-sig")
print("✔ Matched and saved as clean_2015_with_hs.csv")
