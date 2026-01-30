"""
Save Trained Models Script
Run this after training models in the classifier notebook
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score

from app.model_manager import ModelManager, create_model_snapshot

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
PROC_DIR = REPO_ROOT / "data" / "processed"

# Configuration
KEYS = ["student_id", "code_module", "code_presentation"]
TARGET_COL = "target_pass"
IDENTIFIER_COLS = ["student_id", "code_module", "code_presentation", "week"]

LEAKAGE_COLS = [
    "date_unregistration",
    "final_result",
    "target_score",
    "target_score_norm",
]

ASSESSMENT_COLS = [
    "weight_covered",
    "weight_covered_assess",
    "total_weight_assess",
    "remaining_weight_assess",
    "max_possible_final_score_assess",
    "mathematically_impossible_to_pass",
    "weighted_score_assess",
    "cumulative_weighted_score_assess",
    "weighted_score_week",
    "weight_covered_week",
]

DEMOGRAPHIC_COLS = [
    "highest_education", "num_of_prev_attempts", "studied_credits",
    "module_presentation_length", "date_registration",
]

PERSONAL_INFO_COLS = [
    "gender", "region", "imd_band", "age_band", "disability",
]


def build_xy_for_week_snapshot(df, t, *, drop_cols=None, target_col=TARGET_COL):
    """One row per (student_id, module, presentation) using latest week <= t."""
    d = df[df["week"] <= t].copy()
    d = d.sort_values(KEYS + ["week"])
    d = d.groupby(KEYS, as_index=False).tail(1)

    d = d[d[target_col].notna()].copy()
    d[target_col] = d[target_col].astype(int)

    groups = d["student_id"].copy()

    drops = set(LEAKAGE_COLS) | set(IDENTIFIER_COLS)
    if drop_cols:
        drops |= set(drop_cols)

    drops.discard(target_col)

    d = d.drop(columns=[c for c in drops if c in d.columns], errors="ignore")

    still_in = sorted((set(LEAKAGE_COLS) | set(IDENTIFIER_COLS)) & set(d.columns))
    if still_in:
        raise ValueError(f"Leakage/ID columns still present: {still_in}")

    y = d[target_col].copy()
    X = d.drop(columns=[target_col])

    return X, y, groups


def make_preprocessor(X):
    num_cols = X.select_dtypes(include=["int64", "int32", "float64", "float32"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    num_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])

    cat_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer(
        transformers=[
            ("num", num_pipe, num_cols),
            ("cat", cat_pipe, cat_cols),
        ],
        remainder="drop",
    )


def group_train_test_split(X, y, groups, test_size=0.2, random_state=42):
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    return X.iloc[train_idx], X.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]


def train_and_save_models(week=10):
    """
    Train models for a specific week and save them
    
    Args:
        week: Week to train models for (default: 10 - mid-course)
    """
    print(f"Training models for week {week}...")
    
    # Load data
    df = pd.read_csv(PROC_DIR / "ews_feature_store.csv")
    print(f"Loaded {len(df):,} rows")
    
    # Define experiments
    experiments = {
        "E4_full_realistic": {
            "drop_cols": LEAKAGE_COLS + PERSONAL_INFO_COLS,
            "notes": "All non-leaking features (best model)",
        },
    }
    
    # Define models
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1),
        "LogisticRegression": LogisticRegression(max_iter=2000, random_state=42),
    }
    
    manager = ModelManager()
    
    for exp_name, exp_config in experiments.items():
        for model_name, model in models.items():
            print(f"\nTraining {exp_name} | {model_name}...")
            
            # Build features
            X, y, groups = build_xy_for_week_snapshot(
                df, week, drop_cols=exp_config["drop_cols"]
            )
            
            # Split
            X_train, X_test, y_train, y_test = group_train_test_split(
                X, y, groups, test_size=0.2, random_state=42
            )
            
            # Build pipeline
            pipe = Pipeline(steps=[
                ("prep", make_preprocessor(X_train)),
                ("model", model),
            ])
            
            # Train
            pipe.fit(X_train, y_train)
            
            # Evaluate
            y_pred = pipe.predict(X_test)
            y_proba = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else None
            
            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "f1": float(f1_score(y_test, y_pred)),
            }
            
            if y_proba is not None:
                metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
            
            print(f"  Accuracy: {metrics['accuracy']:.3f}")
            print(f"  F1: {metrics['f1']:.3f}")
            if 'roc_auc' in metrics:
                print(f"  ROC-AUC: {metrics['roc_auc']:.3f}")
            
            # Save model
            snapshot_name = create_model_snapshot(
                df=df,
                model=pipe,
                week=week,
                experiment_name=exp_name,
                model_name=model_name,
                metrics=metrics,
                feature_names=X.columns.tolist()
            )
            
            print(f"  ✓ Saved as: {snapshot_name}")
    
    print("\n" + "="*60)
    print("Model training complete!")
    print("Available models:", manager.list_models())
    print("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train and save models")
    parser.add_argument("--week", type=int, default=10, help="Week to train for (default: 10)")
    
    args = parser.parse_args()
    
    train_and_save_models(week=args.week)
