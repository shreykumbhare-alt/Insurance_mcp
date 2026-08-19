import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 5000

# Generating core features
customer_tenure = np.random.randint(1, 120, n_samples)  # months
claim_type = np.random.choice(
    ["Auto", "Health", "Property"], size=n_samples, p=[0.5, 0.3, 0.2]
)
geography = np.random.choice(["Urban", "Suburban", "Rural"], size=n_samples)
provider_id = [f"PRV_{np.random.randint(100, 150)}" for _ in range(n_samples)]

# Financials & Claim History
avg_hist_claim = np.random.normal(3000, 1000, n_samples).clip(500)
claim_amount = avg_hist_claim * np.random.uniform(0.5, 3.0, n_samples)
deviation_from_peer = claim_amount - avg_hist_claim

claims_last_12m = np.random.poisson(0.8, n_samples)
prev_rejected = np.random.binomial(1, 0.1, n_samples)
submission_delay = np.random.exponential(10, n_samples).astype(int)  # days

# Generate Fraud Target (Ground Truth logic with realistic correlations)
fraud_probability = (
    0.05
    + 0.25 * (deviation_from_peer > 3000)
    + 0.20 * (submission_delay > 30)
    + 0.15 * (claims_last_12m > 2)
    + 0.15 * (prev_rejected == 1)
    + 0.10 * (customer_tenure < 6)
)
fraud_probability = np.clip(fraud_probability, 0, 0.95)
is_fraud = np.random.binomial(1, fraud_probability)

# Assemble DataFrame
df = pd.DataFrame(
    {
        "claim_id": [f"CLM_{i+10000}" for i in range(n_samples)],
        "claim_amount": np.round(claim_amount, 2),
        "claim_type": claim_type,
        "customer_tenure": customer_tenure,
        "claims_last_12m": claims_last_12m,
        "avg_hist_claim": np.round(avg_hist_claim, 2),
        "provider_id": provider_id,
        "geography": geography,
        "submission_delay": submission_delay,
        "previously_rejected_claims": prev_rejected,
        "deviation_from_peer_claims": np.round(deviation_from_peer, 2),
        "is_fraud": is_fraud,
    }
)

df.to_csv("insurance_claims_dataset.csv", index=False)
print("Dataset created! Total shape:", df.shape)
print("Fraud distribution:\n", df["is_fraud"].value_counts(normalize=True))