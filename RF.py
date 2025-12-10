import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import shap 

df = pd.read_csv("panel_data/2008after.csv")
drop_cols = [
    'pro_name', 'city_clean', 'is_beijing', 'is_shanghai',
    'pro_name_true', 'English_name', 'hs_residence',
    'lowest_temp(Jan)_a', 'average_temp_a', 'highest_temp(July)_a', 'precipitation(mm)_a',
    'gdp per capita(k)_a', 'unemployment(%)_a', 'education_budget(10k)_a',
    'marriage(10k)_a', 'population(10k)_a', 'Medical technicians per 10k_a',
    'road_length_per_10K (km)_a', 'manageable_income_per_capita_a',
    'Migrate', 'Migrate_1', 'Migrate_2'
]
df = df.drop(columns=drop_cols, errors='ignore')

y = df['pro_code'].astype(str)
X = df.drop(columns=['pro_code'], errors='ignore')
X = X.fillna(0)
X = pd.get_dummies(X, drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
with open('2008after_report_new.txt', 'w') as f:
    f.write("Classification Report:\n")
    f.write(classification_report(y_test, y_pred))

importances = rf.feature_importances_
feat_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Top 10
top10 = feat_importance.head(10)
top10.to_csv("2008after_top10_migration_factors.csv", index=False)
print("\nTop 10 most important indicators saved in: 2008after_top10_migration_factors.csv")

plt.figure(figsize=(8, 6))
sns.barplot(data=top10, x='Importance', y='Feature', palette='viridis')
plt.title("Top 10 Determinants after 2008", fontsize=13)
plt.xlabel("Importance", fontsize=11)
plt.ylabel("Feature", fontsize=11)
plt.tight_layout()
plt.savefig("2008after_top10_migration_factors_RF.jpg", dpi=300, format='jpg')
plt.close()



# sample data
sample_data = X_test.sample(n=min(500, len(X_test)), random_state=42)
feature_names = list(sample_data.columns)

explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(sample_data)

# For multi-class SHAP, average over classes
if isinstance(shap_values, list):
    per_class_abs = [np.mean(np.abs(sv), axis=0) for sv in shap_values]
    per_class_mean = [np.mean(sv, axis=0) for sv in shap_values]
    shap_abs_mean = np.mean(per_class_abs, axis=0)
    shap_mean_direction = np.mean(per_class_mean, axis=0)
else:
    shap_abs_mean = np.mean(np.abs(shap_values), axis=0)
    shap_mean_direction = np.mean(shap_values, axis=0)

shap_abs_mean = shap_abs_mean.flatten()
shap_mean_direction = shap_mean_direction.flatten()

# Combine into list
feat_info = list(zip(feature_names, shap_abs_mean.tolist(), shap_mean_direction.tolist()))
feat_info_sorted = sorted(feat_info, key=lambda x: x[1], reverse=True)

top_n = 20

# Save top SHAP results
with open("SHAP_after.txt", "w", encoding="utf-8") as f:
    f.write("Feature\tMean|SHAP|\tMeanSHAP(Direction)\tInterpretation\n")
    for name, abs_val, dir_val in feat_info_sorted[:top_n]:
        direction = "Positive (promotes target)" if dir_val > 0 else "Negative (reduces target)"
        f.write(f"{name}\t{abs_val:.6f}\t{dir_val:+.6f}\t{direction}\n")

print(f"Saved top {top_n} SHAP features to: SHAP_after.txt")

# =========== PLOT: Top 10 SHAP bar chart ===========
top10 = feat_info_sorted[:10]
names = [t[0] for t in top10][::-1]
vals = [t[1] for t in top10][::-1]
dirs = [t[2] for t in top10][::-1]

colors = ['tab:blue' if d > 0 else 'tab:red' for d in dirs]

plt.figure(figsize=(8, 6))
plt.barh(names, vals, color=colors)
plt.xlabel("Mean |SHAP Value|")
plt.title("Top 10 SHAP Feature Importance (color = direction)")

# print directional shap values with enough precision
for i, (v, d) in enumerate(zip(vals, dirs)):
    sign = "↑" if d > 0 else "↓"
    plt.text(v * 1.02, i, f"{sign} {d:+.6f}", va='center', fontsize=9)

plt.tight_layout()
plt.savefig("SHAP_after_top10_with_direction.jpg", dpi=300)
plt.close()
print("Saved SHAP top10 plot.")

# ================= SHAP summary plot ==================
try:
    shap.summary_plot(shap_values, sample_data, plot_type="dot", show=False)
    plt.savefig("SHAP_after_summary_plot.jpg", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved SHAP summary plot.")
except Exception as e:
    print("Warning: SHAP summary plot failed:", e)