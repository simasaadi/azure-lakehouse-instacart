from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
SEED_DIR = REPO_ROOT / "data" / "seed"
SEED_DIR.mkdir(parents=True, exist_ok=True)

# Very small seed (commit-friendly)
N_ORDERS = 5_000
N_PRIOR = 20_000
N_TRAIN = 5_000
SEED = 42

def main() -> None:
    # dims
    for f in ["aisles.csv", "departments.csv", "products.csv"]:
        (SEED_DIR / f).write_bytes((RAW_DIR / f).read_bytes())

    orders = pd.read_csv(RAW_DIR / "orders.csv")
    orders_s = orders.sample(n=min(N_ORDERS, len(orders)), random_state=SEED)
    orders_s.to_csv(SEED_DIR / "orders.csv", index=False)
    order_ids = set(orders_s["order_id"].astype(int).tolist())

    prior = pd.read_csv(RAW_DIR / "order_products__prior.csv")
    prior_f = prior[prior["order_id"].isin(order_ids)]
    prior_s = prior_f.sample(n=min(N_PRIOR, len(prior_f)), random_state=SEED) if len(prior_f) else prior_f
    prior_s.to_csv(SEED_DIR / "order_products__prior.csv", index=False)

    train = pd.read_csv(RAW_DIR / "order_products__train.csv")
    train_f = train[train["order_id"].isin(order_ids)]
    train_s = train_f.sample(n=min(N_TRAIN, len(train_f)), random_state=SEED) if len(train_f) else train_f
    train_s.to_csv(SEED_DIR / "order_products__train.csv", index=False)

    print("Done ✅ Seed dataset written to data/seed/")

if __name__ == "__main__":
    main()
