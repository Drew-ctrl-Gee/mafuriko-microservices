"""
MafurikoAI - Milestone 3
Data Preprocessing & Feature Engineering
Cleans, transforms, and prepares data for ML training
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

print("=" * 70)
print("   🔧 MAFURIKO AI - DATA PREPROCESSING")
print("   Milestone 3: Feature Engineering")
print("=" * 70)

# ═══════════════════════════════════════════════════════════
# STEP 1: LOAD DATA
# ═══════════════════════════════════════════════════════════

print("\n📂 Loading raw dataset...")
df = pd.read_csv("data/raw/kenya_flood_data.csv")
print(f"✅ Loaded {len(df):,} records")
print(f"📊 Columns: {list(df.columns)}")

# ═══════════════════════════════════════════════════════════
# STEP 2: DATA CLEANING
# ═══════════════════════════════════════════════════════════

print("\n🧹 Step 2: Data Cleaning...")

# Check for missing values
print(f"\n   Missing values before cleaning:")
missing = df.isnull().sum()
print(missing[missing > 0] if missing.sum() > 0 else "   ✅ No missing values!")

# Handle missing values (if any)
df = df.dropna(subset=['flood_risk'])

# Remove duplicates
before = len(df)
df = df.drop_duplicates()
print(f"   ✅ Removed {before - len(df)} duplicates")

# ═══════════════════════════════════════════════════════════
# STEP 3: FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════

print("\n🎯 Step 3: Feature Engineering...")

# Create new engineered features
df["is_rainy_season"] = df["month"].apply(
    lambda m: 1 if m in [3, 4, 5, 10, 11, 12] else 0
)
print("   ✅ Created 'is_rainy_season' feature")

# Composite risk score
df["risk_score"] = (
    (df["rainfall_mm"] / 120 * 3) +
    (df["previous_day_rainfall_mm"] / 80 * 2) +
    ((1 / (df["proximity_to_river_km"] + 0.1)) * 0.5) +
    (df["humidity_percent"] / 100)
)
print("   ✅ Created 'risk_score' composite feature")

# Rainfall category
df["rainfall_category"] = pd.cut(
    df["rainfall_mm"],
    bins=[0, 25, 50, 80, 200],
    labels=["light", "moderate", "heavy", "extreme"]
)
print("   ✅ Created 'rainfall_category' feature")

# ═══════════════════════════════════════════════════════════
# STEP 4: CATEGORICAL ENCODING
# ═══════════════════════════════════════════════════════════

print("\n🔤 Step 4: Encoding Categorical Variables...")

le_drainage = LabelEncoder()
le_road_surface = LabelEncoder()
le_time = LabelEncoder()
le_population = LabelEncoder()
le_county = LabelEncoder()
le_rainfall_cat = LabelEncoder()
le_target = LabelEncoder()

df["drainage_encoded"] = le_drainage.fit_transform(df["drainage_quality"])
df["road_surface_encoded"] = le_road_surface.fit_transform(df["road_surface"])
df["time_encoded"] = le_time.fit_transform(df["time_of_day"])
df["population_encoded"] = le_population.fit_transform(df["population_density"])
df["county_encoded"] = le_county.fit_transform(df["county"])
df["rainfall_cat_encoded"] = le_rainfall_cat.fit_transform(df["rainfall_category"].astype(str))
df["flood_risk_encoded"] = le_target.fit_transform(df["flood_risk"])

print(f"   ✅ Encoded 7 categorical variables")

# ═══════════════════════════════════════════════════════════
# STEP 5: FEATURE SELECTION
# ═══════════════════════════════════════════════════════════

print("\n🎯 Step 5: Feature Selection...")

features = [
    "rainfall_mm",
    "drainage_encoded",
    "elevation_m",
    "proximity_to_river_km",
    "road_surface_encoded",
    "time_encoded",
    "month",
    "temperature_c",
    "humidity_percent",
    "previous_day_rainfall_mm",
    "population_encoded",
    "county_encoded",
    "is_rainy_season",
    "risk_score",
    "rainfall_cat_encoded"
]

X = df[features]
y = df["flood_risk_encoded"]

print(f"   ✅ Selected {len(features)} features")
print(f"   📊 Target classes: {list(le_target.classes_)}")

# ═══════════════════════════════════════════════════════════
# STEP 6: TRAIN/VAL/TEST SPLIT
# ═══════════════════════════════════════════════════════════

print("\n📊 Step 6: Splitting Data...")

# First split: 80% train+val, 20% test
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Second split: 80% train, 20% validation
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.2, random_state=42, stratify=y_temp
)

print(f"   📈 Training set:   {len(X_train):,} samples (64%)")
print(f"   📊 Validation set: {len(X_val):,} samples (16%)")
print(f"   📉 Test set:       {len(X_test):,} samples (20%)")

# ═══════════════════════════════════════════════════════════
# STEP 7: FEATURE SCALING
# ═══════════════════════════════════════════════════════════

print("\n⚖️  Step 7: Feature Scaling...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

print(f"   ✅ Applied StandardScaler to all features")

# ═══════════════════════════════════════════════════════════
# STEP 8: SAVE ARTIFACTS
# ═══════════════════════════════════════════════════════════

print("\n💾 Step 8: Saving Preprocessing Artifacts...")

os.makedirs("models", exist_ok=True)

# Save encoders
joblib.dump(le_drainage, "models/le_drainage.pkl")
joblib.dump(le_road_surface, "models/le_road_surface.pkl")
joblib.dump(le_time, "models/le_time.pkl")
joblib.dump(le_population, "models/le_population.pkl")
joblib.dump(le_county, "models/le_county.pkl")
joblib.dump(le_rainfall_cat, "models/le_rainfall_cat.pkl")
joblib.dump(le_target, "models/le_target.pkl")

# Save scaler
joblib.dump(scaler, "models/scaler.pkl")

# Save features list
joblib.dump(features, "models/features.pkl")

# Save processed data
np.savez(
    "data/processed/train_val_test_data.npz",
    X_train=X_train_scaled,
    X_val=X_val_scaled,
    X_test=X_test_scaled,
    y_train=y_train.values,
    y_val=y_val.values,
    y_test=y_test.values
)

print("   ✅ Saved all encoders (7 files)")
print("   ✅ Saved scaler")
print("   ✅ Saved features list")
print("   ✅ Saved train/val/test data")

# ═══════════════════════════════════════════════════════════
# STEP 9: VISUALIZATIONS
# ═══════════════════════════════════════════════════════════

print("\n📊 Step 9: Creating Visualizations...")

os.makedirs("data/visualizations", exist_ok=True)

# 1. Class distribution
plt.figure(figsize=(10, 6))
risk_counts = df["flood_risk"].value_counts()
colors = ['#00CC66', '#FF8C00', '#FF0000']
plt.bar(risk_counts.index, risk_counts.values, color=colors, edgecolor='black')
plt.title("Flood Risk Distribution in Dataset", fontsize=14, fontweight='bold')
plt.xlabel("Risk Level")
plt.ylabel("Count")
for i, v in enumerate(risk_counts.values):
    plt.text(i, v + 20, str(v), ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig("data/visualizations/class_distribution.png", dpi=150)
plt.close()
print("   ✅ Class distribution chart")

# 2. Rainfall by risk
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="flood_risk", y="rainfall_mm", 
            order=["low", "medium", "high"],
            palette={"low": "#00CC66", "medium": "#FF8C00", "high": "#FF0000"})
plt.title("Rainfall by Flood Risk Level", fontsize=14, fontweight='bold')
plt.xlabel("Flood Risk")
plt.ylabel("Rainfall (mm)")
plt.tight_layout()
plt.savefig("data/visualizations/rainfall_by_risk.png", dpi=150)
plt.close()
print("   ✅ Rainfall analysis chart")

# 3. Correlation heatmap
plt.figure(figsize=(12, 10))
numeric_cols = ["rainfall_mm", "elevation_m", "proximity_to_river_km",
                "temperature_c", "humidity_percent", "previous_day_rainfall_mm",
                "risk_score", "is_rainy_season", "flood_risk_encoded"]
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap="RdBu_r", center=0, fmt=".2f",
            square=True, linewidths=1)
plt.title("Feature Correlation Heatmap", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("data/visualizations/correlation_heatmap.png", dpi=150)
plt.close()
print("   ✅ Correlation heatmap")

# 4. County risk distribution
plt.figure(figsize=(14, 8))
top_counties = df.groupby("county")["flood_occurred"].sum().sort_values(ascending=False).head(15)
plt.barh(top_counties.index[::-1], top_counties.values[::-1], color='crimson', edgecolor='black')
plt.title("Top 15 Flood-Prone Counties", fontsize=14, fontweight='bold')
plt.xlabel("Flood Occurrences")
plt.tight_layout()
plt.savefig("data/visualizations/top_counties.png", dpi=150)
plt.close()
print("   ✅ Top counties chart")

# ═══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("   ✅ PREPROCESSING COMPLETE!")
print("=" * 70)

print(f"\n📊 Dataset Stats:")
print(f"   Total records: {len(df):,}")
print(f"   Features: {len(features)}")
print(f"   Target classes: {len(le_target.classes_)}")

print(f"\n📈 Data Splits:")
print(f"   Training:   {len(X_train):,} ({len(X_train)/len(df)*100:.0f}%)")
print(f"   Validation: {len(X_val):,} ({len(X_val)/len(df)*100:.0f}%)")
print(f"   Testing:    {len(X_test):,} ({len(X_test)/len(df)*100:.0f}%)")

print(f"\n💾 Saved Files:")
print(f"   models/ - 9 artifact files")
print(f"   data/processed/ - Train/Val/Test data")
print(f"   data/visualizations/ - 4 charts")

print("\n🎯 Ready for Milestone 4: Model Training!")
print("=" * 70)