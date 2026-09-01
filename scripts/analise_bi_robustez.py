# -*- coding: utf-8 -*-
"""Robustez + teste estatistico Centro vs Meia Praia + correlacoes nos 999."""
import numpy as np
import pandas as pd
from scipy import stats

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)

DATA = "data"


def norm_suburb(s):
    if pd.isna(s):
        return "NAO_INFORMADO"
    s = str(s).strip().lower()
    s = s.replace("são", "sao").replace("ã", "a").replace("á", "a").replace("é", "e")
    return s.title()


def load(name):
    return pd.read_csv(f"{DATA}/{name}", encoding="utf-8-sig", low_memory=False)


def bucket_bedrooms(n):
    if n <= 1:
        return "Studio/1q"
    if n == 2:
        return "2q"
    return "3q+"


def load_base(price_cap=5000):
    details = load("Details_Itapema.csv")
    mesh = load("Mesh_Ids_Data_Itapema.csv")
    prices = load("Price_AV_Itapema.csv")
    vivareal = load("VivaReal_Itapema.csv")

    mesh["suburb_norm"] = mesh["suburb"].map(norm_suburb)
    details = details.merge(mesh[["airbnb_listing_id", "suburb_norm"]], on="airbnb_listing_id", how="left")

    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    p_list = (prices[prices["price"] <= price_cap]
              .groupby("airbnb_listing_id")
              .agg(adr=("price", "mean")).reset_index())

    perfil = details[["airbnb_listing_id", "number_of_bedrooms", "suburb_norm"]].copy()
    perfil["perfil"] = perfil["number_of_bedrooms"].map(bucket_bedrooms)
    analise = perfil.merge(p_list, on="airbnb_listing_id", how="inner")

    vivareal["suburb_norm"] = vivareal["suburb"].map(norm_suburb)
    vivareal["perfil"] = vivareal["bedrooms"].map(bucket_bedrooms)
    vr = vivareal[(vivareal["listing_type"] == "apartamento")
                  & (vivareal["sale_price"] >= 50000)
                  & (vivareal["usable_area"] <= 1500)]
    compra = (vr.groupby(["suburb_norm", "perfil"])["sale_price"]
              .agg(preco_mediana="median", preco_media="mean", n_ofertas="count").reset_index())
    analise = analise.merge(compra, on=["suburb_norm", "perfil"], how="left")
    return analise


base = load_base(5000).dropna(subset=["preco_mediana"])
base["roi_60"] = base["adr"] * 365 * 0.6 / base["preco_mediana"] * 100
print(f"Base (cap 5000): n={len(base)}")


def roi_combo(df, bair, perf):
    s = df[(df["suburb_norm"] == bair) & (df["perfil"] == perf)]["roi_60"] if bair else df[df["perfil"] == perf]["roi_60"]
    return float(np.median(s)), int(len(s))


combos = {"Studio/1q Centro": ("Centro", "Studio/1q"),
          "2q Centro": ("Centro", "2q"),
          "3q+ geral": (None, "3q+")}

print("\n=== TESTE 1: Outliers > R$ 3.000 vs R$ 5.000 ===")
r1 = load_base(3000).dropna(subset=["preco_mediana"])
r1["roi_60"] = r1["adr"] * 365 * 0.6 / r1["preco_mediana"] * 100
print(f"Base(3k): n={len(r1)}")
for lab, (bair, perf) in combos.items():
    a = roi_combo(base, bair, perf)
    b = roi_combo(r1, bair, perf)
    print(f"  {lab:<18} base(5k): {a[0]:.2f}% (n={a[1]})  |  robusto(3k): {b[0]:.2f}% (n={b[1]})")

print("\n=== TESTE 2: preco MEDIO vs MEDIANO de compra ===")
base_m = base.copy()
base_m["roi_60"] = base_m["adr"] * 365 * 0.6 / base_m["preco_media"] * 100
for lab, (bair, perf) in combos.items():
    s = base_m[(base_m["suburb_norm"] == bair) & (base_m["perfil"] == perf)]["roi_60"] if bair else base_m[base_m["perfil"] == perf]["roi_60"]
    print(f"  {lab:<18} preco medio: {np.median(s):.2f}% (n={len(s)})")

print("\n=== TESTE 3: ocupacao 55% ===")
for lab, (bair, perf) in combos.items():
    s = base[(base["suburb_norm"] == bair) & (base["perfil"] == perf)]["roi_60"] if bair else base[base["perfil"] == perf]["roi_60"]
    print(f"  {lab:<18} @55%: {np.median(s) * 55 / 60:.2f}%")

print("\n=== TESTE 4: Centro vs Meia Praia (Studio/1q) - ROI individual ===")
s_c = base[(base["suburb_norm"] == "Centro") & (base["perfil"] == "Studio/1q")]["roi_60"].dropna().values
s_m = base[(base["suburb_norm"] == "Meia Praia") & (base["perfil"] == "Studio/1q")]["roi_60"].dropna().values
print(f"Centro n={len(s_c)} med={np.median(s_c):.3f} | Meia Praia n={len(s_m)} med={np.median(s_m):.3f}")
t, p = stats.ttest_ind(s_c, s_m, equal_var=False)
print(f"Teste t (Welch): t={t:.4f}, p-valor={p:.6f}")
u, pm = stats.mannwhitneyu(s_c, s_m, alternative="two-sided")
print(f"Mann-Whitney U: U={u:.1f}, p-valor={pm:.6f}")
rng = np.random.default_rng(123)
diffs = np.array([np.median(rng.choice(s_c, len(s_c), replace=True))
                  - np.median(rng.choice(s_m, len(s_m), replace=True))
                  for _ in range(5000)])
ic = np.percentile(diffs, [2.5, 97.5])
print(f"Diferenca bootstrap (Centro - Meia): {np.median(diffs):.3f} p.p. | IC 95%: [{ic[0]:.3f}, {ic[1]:.3f}]")
# mesma comparacao para 2q
q_c = base[(base["suburb_norm"] == "Centro") & (base["perfil"] == "2q")]["roi_60"].dropna().values
q_m = base[(base["suburb_norm"] == "Meia Praia") & (base["perfil"] == "2q")]["roi_60"].dropna().values
print(f"\n(adicional) 2q Centro n={len(q_c)} med={np.median(q_c):.3f} | 2q Meia n={len(q_m)} med={np.median(q_m):.3f}")
t2, p2 = stats.ttest_ind(q_c, q_m, equal_var=False)
print(f"Teste t (Welch): t={t2:.4f}, p-valor={p2:.6f}")

print("\n=== CORRELACOES NOS 999 (robustez secao 4) ===")
details = load("Details_Itapema.csv")
mesh = load("Mesh_Ids_Data_Itapema.csv")
prices = load("Price_AV_Itapema.csv")
mesh["suburb_norm"] = mesh["suburb"].map(norm_suburb)
details = details.merge(mesh[["airbnb_listing_id", "suburb_norm"]], on="airbnb_listing_id", how="left")
prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
p_list999 = prices[prices["price"] <= 5000].groupby("airbnb_listing_id").agg(adr=("price", "mean")).reset_index()
d999 = details[details["airbnb_listing_id"].isin(p_list999["airbnb_listing_id"])].merge(p_list999, on="airbnb_listing_id", how="inner")
print(f"n (correlacoes 999): {len(d999)}")
feats = ["number_of_bedrooms", "number_of_bathrooms", "number_of_guests",
         "cleaning_fee", "number_of_beds", "number_of_reviews",
         "location_rating", "picture_count", "star_rating"]
corr999 = d999[feats + ["adr"]].corr(method="spearman")["adr"].drop("adr")
print(corr999.round(3).to_string())
print("\nComparacao com amostra 972 (do script principal):")
corr972 = pd.Series({
    "number_of_bedrooms": 0.60, "number_of_bathrooms": 0.55, "number_of_guests": 0.52,
    "cleaning_fee": 0.42, "number_of_beds": 0.39, "location_rating": 0.19,
    "picture_count": 0.20, "number_of_reviews": -0.18, "star_rating": 0.08})
for c in feats:
    print(f"  {c:<24} 999={corr999[c]:+.3f} | 972={corr972.get(c, float('nan')):+.3f} | variacao={abs(corr999[c]-corr972.get(c,0)):.3f}")