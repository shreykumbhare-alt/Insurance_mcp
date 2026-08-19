import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    roc_auc_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
)
import lightgbm as lgb


def main():
    # 1. Load Dataset
    data_path = "insurance_claims_dataset.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Dataset '{data_path}' not found. Please ensure the CSV file exists."
        )

    df = pd.read_csv(data_path)
    print(f"Loaded dataset with shape: {df.shape}")

    # 2. Define Features & Target
    categorical_cols = ["claim_type", "geography"]
    numeric_cols = [
        "claim_amount",
        "customer_tenure",
        "claims_last_12m",
        "avg_hist_claim",
        "submission_delay",
        "previously_rejected_claims",
        "deviation_from_peer_claims",
    ]
    
    # Provider ID frequency encoding (turns high-cardinality provider IDs into useful signals)
    provider_counts = df["provider_id"].value_counts().to_dict()
    df["provider_claim_freq"] = df["provider_id"].map(provider_counts)
    numeric_cols.append("provider_claim_freq")

    X_num = df[numeric_cols].values
    X_cat = df[categorical_cols]

    # One-Hot Encoding for categorical variables
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    X_cat_encoded = encoder.fit_transform(X_cat)
    cat_feature_names = list(encoder.get_feature_names_out(categorical_cols))

    # Combine preprocessed features
    X = np.hstack([X_num, X_cat_encoded])
    feature_names = numeric_cols + cat_feature_names
    y = df["is_fraud"].values

    print(f"Total features after encoding: {len(feature_names)}")

    # 3. Train-Test Split (Stratified to maintain fraud ratio)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train Model (LightGBM)
    # scale_pos_weight balances the class weights for fraud detection
    scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)

    model = lgb.LGBMClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=5,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        verbosity=-1,
    )

    model.fit(X_train, y_train)

    # 5. Model Evaluation
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    auc_score = roc_auc_score(y_test, y_pred_proba)
    print("\n" + "=" * 40)
    print(f"   ROC-AUC Score: {auc_score:.4f}")
    print("=" * 40)
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Fraud"]))

    # 6. Feature Importance Quick Inspection
    feature_importances = pd.Series(
        model.feature_importances_, index=feature_names
    ).sort_values(ascending=False)
    print("Top 5 Most Important Features:")
    print(feature_importances.head(5))

    # 7. Persist Model Artifacts Locally
    os.makedirs("models", exist_ok=True)

    joblib.dump(model, "models/fraud_model.joblib")
    joblib.dump(encoder, "models/categorical_encoder.joblib")
    joblib.dump(provider_counts, "models/provider_counts.joblib")

    artifact_meta = {
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "feature_names": feature_names,
    }
    with open("models/metadata.json", "w") as f:
        json.dump(artifact_meta, f, indent=2)

    print("\n✅ All model artifacts successfully saved to './models/' folder:")
    print("   - models/fraud_model.joblib")
    print("   - models/categorical_encoder.joblib")
    print("   - models/provider_counts.joblib")
    print("   - models/metadata.json")
    
if __name__ == "__main__":
    main()