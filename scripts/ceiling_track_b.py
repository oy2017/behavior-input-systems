"""Supervised information ceiling for Track B (no LLM): predict the target-game choice from the subject's
history-game choices with a HistGradientBoosting model, 5-fold CV over records; plus reference errors
(uniform guess, random human draw) and the bootstrap lower bound on W. Mirrors Jackson et al. Fig. 7."""
from __future__ import annotations
import json, sys, collections
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.games import ROLES, RANGE, LABEL2ROLE, normalize

recs = [json.loads(l) for l in Path("data/track_b_subjects.jsonl").read_text().splitlines()]
hist_roles = [r for r in ROLES if r != "push_pull"]
out = {}
print(f"{'game':20s} {'n':>5s} {'HistGBT':>8s} {'uniform':>8s} {'rand_hum':>8s} {'W_floor':>8s}")
for game in ROLES:
    rs = [r for r in recs if r["target_game"] == game]
    if game == "push_pull":
        continue
    X = np.full((len(rs), len(hist_roles)), np.nan); y = np.zeros(len(rs))
    for i, r in enumerate(rs):
        y[i] = normalize(float(r["target_answer"]), game)
        for h in r["history"]:
            try: X[i, hist_roles.index(LABEL2ROLE[h["label"]])] = normalize(float(h["choice"]), LABEL2ROLE[h["label"]])
            except ValueError: pass
    keep = ~np.all(np.isnan(X), axis=0); X = X[:, keep]  # drop the target role's own column (always NaN) and unused roles
    pred = np.zeros(len(rs))
    for tr, te in KFold(5, shuffle=True, random_state=0).split(X):
        m = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, random_state=0).fit(X[tr], y[tr]); pred[te] = m.predict(X[te])
    mae = np.mean(np.abs(pred - y))
    grid = np.linspace(0, 100, 101); uniform = np.mean([np.mean(np.abs(grid - t)) for t in y])
    rand_hum = np.mean(np.abs(y[:, None] - y[None, :])[~np.eye(len(y), dtype=bool)])
    rng = np.random.default_rng(0); wf = np.mean([wasserstein_distance(y, rng.choice(y, len(y))) for _ in range(200)])
    out[game] = {"n": len(rs), "histgbt_mae": mae, "uniform_mae": uniform, "random_human_mae": rand_hum, "W_floor": wf}
    print(f"{game:20s} {len(rs):5d} {mae:8.2f} {uniform:8.2f} {rand_hum:8.2f} {wf:8.2f}")
Path("outputs/track_b/ceiling.json").write_text(json.dumps(out, indent=1))
