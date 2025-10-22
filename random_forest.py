import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# read data
df = pd.read_csv("panel_data/2008before.csv")

# Delete variables that may reveal migration destinations
drop_cols = [
    'pro_name', 'city_clean', 'is_beijing', 'is_shanghai',
    'pro_name_true', 'English_name', 'hs_residence',
    # after_migration(_a)
    'lowest_temp(Jan)_a', 'average_temp_a', 'highest_temp(July)_a', 'precipitation(mm)_a',
    'gdp per capita(k)_a', 'unemployment(%)_a', 'education_budget(10k)_a',
    'marriage(10k)_a', 'population(10k)_a', 'Medical technicians per 10k_a',
    'road_length_per_10K (km)_a', 'manageable_income_per_capita_a',
    'Migrate', 'Migrate_1', 'Migrate_2'
    #'GDP_after_move', 'migration_year', 'migration_interval', 'migration_distance_km',
]
df = df.drop(columns=drop_cols, errors='ignore')

# aim variable
y = df['pro_code'].astype(str)
X = df.drop(columns=['pro_code'], errors='ignore')
X = X.fillna(0)
X = pd.get_dummies(X, drop_first=True)

# split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# random forest model
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
rf.fit(X_train, y_train)

# model evaluation
y_pred = rf.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
with open('2008before_classification_report.txt', 'w') as f:
    f.write("Classification Report:\n")
    f.write(classification_report(y_test, y_pred))

# feature importance analysis
importances = rf.feature_importances_
feat_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Top 10 indicators
top10 = feat_importance.head(10)
top10.to_csv("2008before_top10_migration_factors.csv", index=False)
print("\ntop 10 most important indicators are saved in: top10_migration_factors.csv")

# visualization
plt.figure(figsize=(8, 6))
sns.barplot(data=top10, x='Importance', y='Feature', palette='viridis')
plt.title("Top 10 Determinants of Migration Destination", fontsize=13)
plt.xlabel("Importance", fontsize=11)
plt.ylabel("Feature", fontsize=11)
plt.tight_layout()
plt.savefig("2008before_top10_migration_factors.jpg", dpi=300, format='jpg')
plt.close()
print("The image is saved as: top10_migration_factors.jpg")
