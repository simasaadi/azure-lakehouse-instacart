from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
SAMPLE_DIR = REPO_ROOT / "data" / "sample"

# Keep dims complete (small anyway)
DIM_FILES = [
    "aisles.csv",
    "departments.csv",
    "products.csv",
]

# Sample sizes (tuned for CI speed)
N_ORDERS = 50_000
N_PRIOR = 200_000
N_TRAIN = 50_000

SEED = 42

def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    # Copy dims as-is
    for f in DIM_FILES:
        src = RAW_DIR / f
        dst = SAMPLE_DIR / f
        print(f"Copying {src.name} -> sample/{dst.name}")
        dst.write_bytes(src.read_bytes())

    # Orders: sample N_ORDERS deterministically
    orders = pd.read_csv(RAW_DIR / "orders.csv")
    orders_s = orders.sample(n=min(N_ORDERS, len(orders)), random_state=SEED)
    orders_s.to_csv(SAMPLE_DIR / "orders.csv", index=False)
    order_ids = set(orders_s["order_id"].astype(int).tolist())
    print(f"Sample orders: {len(order_ids):,}")

    # Prior: filter by sampled order_ids, then sample rows
    prior = pd.read_csv(RAW_DIR / "order_products__prior.csv")
    prior_f = prior[prior["order_id"].isin(order_ids)]
    prior_s = prior_f.sample(n=min(N_PRIOR, len(prior_f)), random_state=SEED) if len(prior_f) else prior_f
    prior_s.to_csv(SAMPLE_DIR / "order_products__prior.csv", index=False)
    print(f"Sample prior rows: {len(prior_s):,}")

    # Train: filter by sampled order_ids, then sample rows
    train = pd.read_csv(RAW_DIR / "order_products__train.csv")
    train_f = train[train["order_id"].isin(order_ids)]
    train_s = train_f.sample(n=min(N_TRAIN, len(train_f)), random_state=SEED) if len(train_f) else train_f
    train_s.to_csv(SAMPLE_DIR / "order_products__train.csv", index=False)
    print(f"Sample train rows: {len(train_s):,}")

    print("\nDone ✅ Sample dataset written to data/sample/")

if __name__ == "__main__":
    main()
