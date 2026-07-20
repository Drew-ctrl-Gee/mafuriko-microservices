"""
MafurikoAI - Milestone 4
Model Development & Training
Trains Random Forest classifier for flood prediction
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.model_selection import cross_val_score
import joblib
import os
import warnings
warnings.filterwarnings("ignore")

print("=" * 70)
print("   🤖 MAFURIKO AI - MODEL TRAINING")
print("   Milestone 4: Model Development")
print("=" * 70)

# ═══════════════════════════════════════════════════════════
# STEP 1: LOAD PROCESSED DATA
# ═══════════════════════════════════════════════════════════

print("\n📂 Loading preprocessed data...")

data = np.load("data/processed/train_val_test_data.npz")
X_train = data['X_train']
X_val = data['X_val']
X_test = data['X_test']
y_train = data['y_train']
y_val = data['y_val']
y_test = data['y_test']

features = joblib.load("models/features.pkl")
le_target = joblib.load("models/le_target.pkl")

print(f"✅ Loaded data:")
print(f"   Training: {X_train.shape}")
print(f"   Validation: {X_val.shape}")
print(f"   Testing: {X_test.shape}")

# ═══════════════════════════════════════════════════════════
# STEP 2: TRAIN MULTIPLE MODELS
# ═══════════════════════════════════════════════════════════

print("\n🤖 Training multiple models for comparison...")

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        bootstrap=True,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        random_state=42
    )
}

results = {}

for name, model in models.items():
    print(f"\n   🔧 Training {name}...")
    
    # Train
    model.fit(X_train, y_train)
    
    # Predict on validation set
    y_pred_val = model.predict(X_val)
    y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    val_acc = accuracy_score(y_val, y_pred_val)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    
    results[name] = {
        "model": model,
        "val_accuracy": val_acc,
        "test_accuracy": test_acc,
        "cv_mean": cv_scores.mean(),
        "cv_std": cv_scores.std(),
        "predictions": y_pred_test
    }
    
    print(f"      ✅ Validation Accuracy: {val_acc*100:.2f}%")
    print(f"      ✅ Test Accuracy: {test_acc*100:.2f}%")
    print(f"      ✅ CV Score: {cv_scores.mean()*100:.2f}% (±{cv_scores.std()*100:.2f}%)")

# ═══════════════════════════════════════════════════════════
# STEP 3: SELECT BEST MODEL
# ═══════════════════════════════════════════════════════════

print("\n🏆 Selecting best model...")

best_name = max(results, key=lambda k: results[k]["test_accuracy"])
best_model = results[best_name]["model"]
best_accuracy = results[best_name]["test_accuracy"]

print(f"\n   🎯 BEST MODEL: {best_name}")
print(f"   📊 Test Accuracy: {best_accuracy*100:.2f}%")

# ═══════════════════════════════════════════════════════════
# STEP 4: DETAILED EVALUATION
# ═══════════════════════════════════════════════════════════

print("\n📊 Detailed Model Evaluation...")

y_best_pred = results[best_name]["predictions"]

# Classification report
print(f"\n📋 Classification Report:")
print(classification_report(
    y_test, y_best_pred,
    target_names=le_target.classes_,
    digits=4
))

# Additional metrics
precision = precision_score(y_test, y_best_pred, average='weighted')
recall = recall_score(y_test, y_best_pred, average='weighted')
f1 = f1_score(y_test, y_best_pred, average='weighted')

print(f"\n📈 Performance Metrics:")
print(f"   Precision (weighted): {precision:.4f}")
print(f"   Recall (weighted):    {recall:.4f}")
print(f"   F1-Score (weighted):  {f1:.4f}")

# ═══════════════════════════════════════════════════════════
# STEP 5: VISUALIZATIONS
# ═══════════════════════════════════════════════════════════

print("\n📊 Creating evaluation visualizations...")

os.makedirs("data/visualizations", exist_ok=True)

# 1. Confusion Matrix
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_test, y_best_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=le_target.classes_,
            yticklabels=le_target.classes_,
            cbar_kws={'label': 'Count'})
plt.title(f"Confusion Matrix - {best_name}\nAccuracy: {best_accuracy*100:.2f}%",
          fontsize=14, fontweight='bold')
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("data/visualizations/confusion_matrix.png", dpi=150)
plt.close()
print("   ✅ Confusion matrix")

# 2. Model Comparison
plt.figure(figsize=(12, 6))
model_names = list(results.keys())
val_accs = [results[m]["val_accuracy"] * 100 for m in model_names]
test_accs = [results[m]["test_accuracy"] * 100 for m in model_names]

x = np.arange(len(model_names))
width = 0.35

plt.bar(x - width/2, val_accs, width, label='Validation', color='steelblue', edgecolor='black')
plt.bar(x + width/2, test_accs, width, label='Test', color='crimson', edgecolor='black')

plt.title("Model Comparison", fontsize=14, fontweight='bold')
plt.ylabel("Accuracy (%)")
plt.xticks(x, model_names)
plt.legend()
plt.ylim(0, 105)

for i, (v, t) in enumerate(zip(val_accs, test_accs)):
    plt.text(i - width/2, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
    plt.text(i + width/2, t + 1, f'{t:.1f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("data/visualizations/model_comparison.png", dpi=150)
plt.close()
print("   ✅ Model comparison chart")

# 3. Feature Importance (for Random Forest)
if best_name == "Random Forest" or best_name == "Gradient Boosting":
    plt.figure(figsize=(10, 8))
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.title(f"Feature Importance - {best_name}", fontsize=14, fontweight='bold')
    plt.barh(range(len(importances)), importances[indices][::-1],
             color='teal', edgecolor='black')
    plt.yticks(range(len(importances)), [features[i] for i in indices][::-1])
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig("data/visualizations/feature_importance.png", dpi=150)
    plt.close()
    print("   ✅ Feature importance chart")

# ═══════════════════════════════════════════════════════════
# STEP 6: SAVE MODEL
# ═══════════════════════════════════════════════════════════

print("\n💾 Saving trained model...")

os.makedirs("models", exist_ok=True)

# Save the best model
joblib.dump(best_model, "models/flood_model.pkl")

# Save model metadata
metadata = {
    "model_type": best_name,
    "accuracy": float(best_accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
    "features": features,
    "classes": le_target.classes_.tolist(),
    "training_samples": len(X_train),
    "test_samples": len(X_test),
    "version": "1.0.0"
}

joblib.dump(metadata, "models/model_metadata.pkl")

print(f"   ✅ Model saved: models/flood_model.pkl")
print(f"   ✅ Metadata saved: models/model_metadata.pkl")

# ═══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("   ✅ MODEL TRAINING COMPLETE!")
print("=" * 70)

print(f"\n🏆 Best Model: {best_name}")
print(f"🎯 Test Accuracy: {best_accuracy*100:.2f}%")
print(f"📊 F1-Score: {f1:.4f}")

print(f"\n📁 Model Artifacts:")
print(f"   models/flood_model.pkl")
print(f"   models/model_metadata.pkl")
print(f"   models/*.pkl (encoders & scaler)")

print(f"\n📈 Visualizations:")
print(f"   data/visualizations/confusion_matrix.png")
print(f"   data/visualizations/model_comparison.png")
print(f"   data/visualizations/feature_importance.png")

print("\n🎯 Ready for Milestone 5: Deployment!")
print("=" * 70)