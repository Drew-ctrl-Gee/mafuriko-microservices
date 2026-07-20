"""
MafurikoAI - Milestone 2 & 3
Data Generation & Preprocessing
Generates realistic flood dataset for Kenya
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 70)
print("   🌧️  MAFURIKO AI - DATA GENERATION")
print("   Milestone 2: Data Acquisition")
print("=" * 70)

np.random.seed(42)

# All 47 Kenyan Counties
COUNTIES = {
    "Nairobi": {"elev": (1600, 1800), "flood_prone": True},
    "Mombasa": {"elev": (5, 50), "flood_prone": True},
    "Kisumu": {"elev": (1130, 1300), "flood_prone": True},
    "Nakuru": {"elev": (1800, 2000), "flood_prone": False},
    "Uasin Gishu": {"elev": (2000, 2200), "flood_prone": False},
    "Kiambu": {"elev": (1500, 2100), "flood_prone": False},
    "Machakos": {"elev": (1100, 1700), "flood_prone": False},
    "Kajiado": {"elev": (900, 2000), "flood_prone": False},
    "Nyeri": {"elev": (1700, 2000), "flood_prone": False},
    "Meru": {"elev": (1400, 1800), "flood_prone": False},
    "Kakamega": {"elev": (1300, 1600), "flood_prone": True},
    "Kisii": {"elev": (1500, 2000), "flood_prone": False},
    "Kericho": {"elev": (1900, 2200), "flood_prone": False},
    "Bomet": {"elev": (1900, 2200), "flood_prone": False},
    "Narok": {"elev": (1700, 2200), "flood_prone": False},
    "Kajiado": {"elev": (900, 2000), "flood_prone": False},
    "Turkana": {"elev": (400, 900), "flood_prone": True},
    "Marsabit": {"elev": (300, 1700), "flood_prone": True},
    "Isiolo": {"elev": (700, 1300), "flood_prone": False},
    "Garissa": {"elev": (100, 400), "flood_prone": True},
    "Wajir": {"elev": (200, 500), "flood_prone": True},
    "Mandera": {"elev": (300, 800), "flood_prone": True},
    "Tana River": {"elev": (50, 200), "flood_prone": True},
    "Lamu": {"elev": (0, 30), "flood_prone": True},
    "Kilifi": {"elev": (5, 200), "flood_prone": True},
    "Kwale": {"elev": (10, 800), "flood_prone": True},
    "Taita Taveta": {"elev": (500, 2200), "flood_prone": False},
    "Bungoma": {"elev": (1300, 1900), "flood_prone": False},
    "Busia": {"elev": (1100, 1300), "flood_prone": True},
    "Siaya": {"elev": (1100, 1500), "flood_prone": True},
    "Homa Bay": {"elev": (1100, 1700), "flood_prone": True},
    "Migori": {"elev": (1200, 1500), "flood_prone": False},
    "Nyamira": {"elev": (1600, 2000), "flood_prone": False},
    "Baringo": {"elev": (900, 2300), "flood_prone": False},
    "West Pokot": {"elev": (1000, 2200), "flood_prone": False},
    "Samburu": {"elev": (900, 2000), "flood_prone": False},
    "Trans Nzoia": {"elev": (1800, 2000), "flood_prone": False},
    "Elgeyo Marakwet": {"elev": (1500, 2700), "flood_prone": False},
    "Nandi": {"elev": (1700, 2200), "flood_prone": False},
    "Laikipia": {"elev": (1800, 2100), "flood_prone": False},
    "Nyandarua": {"elev": (2000, 2800), "flood_prone": False},
    "Muranga": {"elev": (1300, 1700), "flood_prone": False},
    "Kirinyaga": {"elev": (1200, 1500), "flood_prone": False},
    "Embu": {"elev": (1300, 1600), "flood_prone": False},
    "Tharaka Nithi": {"elev": (600, 1500), "flood_prone": False},
    "Kitui": {"elev": (1000, 1400), "flood_prone": False},
    "Makueni": {"elev": (900, 1700), "flood_prone": False},
    "Vihiga": {"elev": (1400, 1900), "flood_prone": False},
}

# Major roads
ROADS = [
    "Thika Superhighway", "Mombasa Road", "Waiyaki Way", "Ngong Road",
    "Lang'ata Road", "Jogoo Road", "Outer Ring Road", "Uhuru Highway",
    "Kenyatta Avenue", "River Road", "Nyali Bridge", "Malindi Road",
    "Kakamega Road", "Kondele Road", "Uganda Road", "Nandi Road",
    "Eldoret-Kitale Road", "Kiambu Road", "Limuru Road", "Ruiru Road"
]

print("\n📊 Generating comprehensive Kenya flood dataset...")

data_records = []

for county_name, info in COUNTIES.items():
    # 25 records per county for good training
    for _ in range(25):
        elev_min, elev_max = info["elev"]
        
        record = {
            "county": county_name,
            "road_name": np.random.choice(ROADS),
            "rainfall_mm": round(np.random.uniform(0, 120), 2),
            "drainage_quality": np.random.choice(
                ["poor", "average", "good"],
                p=[0.4, 0.35, 0.25] if info["flood_prone"] else [0.2, 0.4, 0.4]
            ),
            "elevation_m": round(np.random.uniform(elev_min, elev_max), 2),
            "proximity_to_river_km": round(np.random.uniform(0.1, 10), 2),
            "road_surface": np.random.choice(
                ["tarmac", "murram", "concrete"],
                p=[0.6, 0.3, 0.1]
            ),
            "time_of_day": np.random.choice(
                ["morning", "afternoon", "evening", "night"]
            ),
            "month": np.random.randint(1, 13),
            "temperature_c": round(np.random.uniform(14, 32), 2),
            "humidity_percent": round(np.random.uniform(40, 95), 2),
            "previous_day_rainfall_mm": round(np.random.uniform(0, 80), 2),
            "population_density": np.random.choice(
                ["low", "medium", "high"],
                p=[0.3, 0.4, 0.3]
            )
        }
        data_records.append(record)

df = pd.DataFrame(data_records)
print(f"✅ Generated {len(df):,} records across {df['county'].nunique()} counties")

# Assign flood risk labels based on features
def assign_flood_risk(row):
    """Complex logic to assign realistic flood risk"""
    score = 0
    
    # Rainfall impact
    if row["rainfall_mm"] > 80: score += 3
    elif row["rainfall_mm"] > 50: score += 2
    elif row["rainfall_mm"] > 25: score += 1
    
    # Drainage impact
    if row["drainage_quality"] == "poor": score += 2
    elif row["drainage_quality"] == "average": score += 1
    
    # River proximity
    if row["proximity_to_river_km"] < 1: score += 2
    elif row["proximity_to_river_km"] < 3: score += 1
    
    # Elevation
    if row["elevation_m"] < 500: score += 3
    elif row["elevation_m"] < 1000: score += 2
    elif row["elevation_m"] < 1500: score += 1
    
    # Previous rainfall
    if row["previous_day_rainfall_mm"] > 50: score += 2
    elif row["previous_day_rainfall_mm"] > 25: score += 1
    
    # Road surface
    if row["road_surface"] == "murram": score += 1
    
    # Humidity
    if row["humidity_percent"] > 80: score += 1
    
    # Rainy season (March-May, Oct-Dec)
    if row["month"] in [3, 4, 5, 10, 11, 12]: score += 1
    
    # Flood-prone counties
    flood_prone = ["Tana River", "Garissa", "Kisumu", "Busia", 
                    "Mombasa", "Lamu", "Turkana", "Kilifi"]
    if row["county"] in flood_prone: score += 1
    
    # Classify
    if score >= 9: return "high"
    elif score >= 5: return "medium"
    else: return "low"

df["flood_risk"] = df.apply(assign_flood_risk, axis=1)

# Add flood occurred (binary)
def flood_occurred(risk):
    probs = {"high": 0.85, "medium": 0.45, "low": 0.10}
    return int(np.random.random() < probs.get(risk, 0.1))

df["flood_occurred"] = df["flood_risk"].apply(flood_occurred)

# Save datasets
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

df.to_csv("data/raw/kenya_flood_data.csv", index=False)

# Summary
print("\n" + "=" * 70)
print("   ✅ DATA GENERATION COMPLETE!")
print("=" * 70)
print(f"\n📊 Total Records: {len(df):,}")
print(f"🇰🇪 Counties: {df['county'].nunique()}/47")
print(f"🛣️  Roads: {df['road_name'].nunique()}")

print(f"\n📈 Flood Risk Distribution:")
for risk, count in df["flood_risk"].value_counts().items():
    pct = (count / len(df)) * 100
    emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}[risk]
    print(f"   {emoji} {risk.upper()}: {count:,} ({pct:.1f}%)")

print(f"\n🌊 Flood Occurrences:")
print(f"   Yes: {df['flood_occurred'].sum():,}")
print(f"   No:  {(len(df) - df['flood_occurred'].sum()):,}")

print(f"\n📁 Saved to: data/raw/kenya_flood_data.csv")
print(f"📁 File size: {os.path.getsize('data/raw/kenya_flood_data.csv') / 1024:.1f} KB")
print("\n🎯 Ready for Milestone 3: Preprocessing!")
print("=" * 70)