# -*- coding: utf-8 -*-
"""Correcoes BI: sensibilidade de ocupacao, testes estatisticos, IC bootstrap, sazonalidade."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)

DATA = "data"
OUT = "graficos"

NAVY = "#00143D"
AZUL = "#0055FF"
CORAL = "#FC6058"
CINZA = "#8A97AE"

sns.set_theme(style="whitegrid", rc={
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#D5DCE8",
    "axes.linewidth": 0.8,
    "figure.titlesize": 16,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelcolor": NAVY,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})


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


def bootstrap_ci(data, n_boot=5000, seed=42):
    rng = np.random.default_rng(seed)
    meds = np.array([np.median(rng.choice(data, len(data), replace=True))
                     for _ in range(n_boot)])
    return np.percentile(meds, [2.5, 97.5])


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(f"{OUT}/{nome}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  salvou {OUT}/{nome}")


# ------------------------- PREPARACAO -------------------------
print("Preparando dados...")
details = load("Details_Itapema.csv")
hosts = load("Hosts_ids_Itapema.csv")
mesh = load("Mesh_Ids_Data_Itapema.csv")
prices = load("Price_AV_Itapema.csv")
vivareal = load("VivaReal_Itapema.csv")

mesh["suburb_norm"] = mesh["suburb"].map(norm_suburb)
details = details.merge(
    mesh[["airbnb_listing_id", "latitude", "longitude", "suburb_norm"]],
    on="airbnb_listing_id", how="left")

prices = prices[prices["price"] <= 5000]
prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
prices["month"] = prices["date"].dt.month
p_list = (prices.groupby("airbnb_listing_id")
          .agg(noites=("date", "nunique"),
               receita_bruta=("price", "sum"),
               adr=("price", "mean"))
          .reset_index())

hosts = hosts.drop_duplicates(subset="owner_id", keep="first")

perfil = details[["airbnb_listing_id", "number_of_bedrooms", "suburb_norm"]].copy()
perfil["perfil"] = perfil["number_of_bedrooms"].map(bucket_bedrooms)

analise = perfil.merge(p_list, on="airbnb_listing_id", how="inner")

vivareal["suburb_norm"] = vivareal["suburb"].map(norm_suburb)
vivareal["perfil"] = vivareal["bedrooms"].map(bucket_bedrooms)
vr = vivareal[(vivareal["listing_type"] == "apartamento")
              & (vivareal["sale_price"] >= 50000)
              & (vivareal["usable_area"] <= 1500)]
compra = (vr.groupby(["suburb_norm", "perfil"])["sale_price"]
          .agg(preco_mediana="median", n_ofertas="count").reset_index())
analise = analise.merge(compra, on=["suburb_norm", "perfil"], how="left")
analise = analise.dropna(subset=["preco_mediana"])

# ROI individual por listing (cenario 60%) para testes e ICs
analise["roi_60"] = analise["adr"] * 365 * 0.60 / analise["preco_mediana"] * 100
analise["payback_60"] = analise["preco_mediana"] / (analise["adr"] * 365 * 0.60)

print(f"Listings com preco + perfil + bairro + preco de compra: {len(analise)}")

# ------------------------- 1. SENSIBILIDADE DE OCUPACAO -------------------------
print("\n" + "=" * 80)
print("1. ANALISE DE SENSIBILIDADE DE OCUPACAO")
print("=" * 80)

combos = [
    ("Centro", "Studio/1q"),
    ("Centro", "2q"),
    (None, "3q+"),  # 3q+ em todos os bairros
]
occ_cenarios = [0.4, 0.5, 0.6, 0.7, 0.8]
# Base = mediana do ROI_60 individual (mesma metrica das tabelas do relatorio)
roi_base = {}
for bairro, perf_a in combos:
    sub = analise[analise["perfil"] == perf_a]
    if bairro:
        sub = sub[sub["suburb_norm"] == bairro]
    roi_base[(perf_a, bairro or "geral")] = sub["roi_60"].median()  # ROI @60%
    print(f"  base(60%): {perf_a} {'('+bairro+')' if bairro else '(geral)'} -> {roi_base[(perf_a, bairro or 'geral')]:.2f}% (n={len(sub)})")

sens_rows = []
for (perf_a, key), base in roi_base.items():
    for occ in occ_cenarios:
        sens_rows.append({"ocupacao": occ,
                          "combo": f"{perf_a} {'('+key+')' if key!='geral' else '(geral)'}",
                          "roi": base * occ / 0.60})

sens_df = pd.DataFrame(sens_rows)
sens_pivot = sens_df.pivot(index="ocupacao", columns="combo", values="roi")
order_cols = ["Studio/1q (Centro)", "2q (Centro)", "3q+ (geral)"]
sens_pivot = sens_pivot[[c for c in order_cols if c in sens_pivot.columns]]
print(sens_pivot.to_string())

sens_pivot.reset_index().to_csv("metricas/sensibilidade_ocupacao.csv", index=False, encoding="utf-8-sig")

# ------------------------- 2. TESTE ESTATISTICO Studio vs 2q -------------------------
print("\n" + "=" * 80)
print("2. TESTE ESTATISTICO: Studio/1q vs 2q (ROI 60% individual por listing)")
print("=" * 80)
s = analise.loc[analise["perfil"] == "Studio/1q", "roi_60"].dropna().values
q = analise.loc[analise["perfil"] == "2q", "roi_60"].dropna().values
print(f"n Studio/1q = {len(s)}  |  n 2q = {len(q)}")

t_stat, p_valor = stats.ttest_ind(s, q, equal_var=False)  # Welch
print(f"Teste t (Welch): t = {t_stat:.4f}, p-valor = {p_valor:.6f}")

u_stat, p_mw = stats.mannwhitneyu(s, q, alternative="two-sided")
print(f"Mann-Whitney U: U = {u_stat:.1f}, p-valor = {p_mw:.6f}")

ic_s = bootstrap_ci(s)
ic_q = bootstrap_ci(q)
print(f"IC 95% mediana ROI Studio/1q: [{ic_s[0]:.2f} - {ic_s[1]:.2f}]%")
print(f"IC 95% mediana ROI 2q:        [{ic_q[0]:.2f} - {ic_q[1]:.2f}]%")

rng = np.random.default_rng(7)
diffs = np.array([np.median(rng.choice(s, len(s), replace=True))
                  - np.median(rng.choice(q, len(q), replace=True))
                  for _ in range(5000)])
ic_diff = np.percentile(diffs, [2.5, 97.5])
print(f"Diferenca bootstrap (Studio-2q) da mediana: {np.median(diffs):.3f} p.p. | IC 95%: [{ic_diff[0]:.3f}, {ic_diff[1]:.3f}]")

# ------------------------- 3. IC BOOTSTRAP POR BAIRRO -------------------------
print("\n" + "=" * 80)
print("3. INTERVALO DE CONFIANCA BOOTSTRAP POR BAIRRO (ROI 60%)")
print("=" * 80)
bairros_ic = []
for bairro, sub in analise.groupby("suburb_norm"):
    dados = sub["roi_60"].dropna().values
    if len(dados) >= 4:
        ic = bootstrap_ci(dados)
        bairros_ic.append({
            "bairro": bairro,
            "n": len(dados),
            "roi_mediano": round(np.median(dados), 2),
            "ic_inferior": round(ic[0], 2),
            "ic_superior": round(ic[1], 2),
            "amplitude": round(ic[1] - ic[0], 2),
        })
df_ic = pd.DataFrame(bairros_ic).sort_values("roi_mediano", ascending=False)
print(df_ic.to_string(index=False))
df_ic.to_csv("metricas/ic_bairros.csv", index=False, encoding="utf-8-sig")

# ------------------------- 4. GRAFICO 6: SAZONALIDADE -------------------------
print("\n" + "=" * 80)
print("4. GRAFICO 6: Sazonalidade do ADR por bairro")
print("=" * 80)
fig, ax = plt.subplots(figsize=(9, 5))
monthly = prices.merge(details[["airbnb_listing_id", "suburb_norm"]], on="airbnb_listing_id")
monthly = monthly[monthly["suburb_norm"].isin(["Centro", "Meia Praia"])]
pivot_s = monthly.groupby(["month", "suburb_norm"])["price"].median().unstack()
print("ADR mediano por mes (R$):")
print(pivot_s.to_string())
pivot_s.plot(kind="line", ax=ax, marker="o", linewidth=2.2, color=[AZUL, CORAL], zorder=3)
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
ax.axvspan(4.5, 12.5, color="#F0F0F0", alpha=0.55, zorder=0)
ax.text(8.5, 850, "Sem dados\n(fora de jan-abr/2025)", ha="center", va="center",
        fontsize=9, color=CINZA, style="italic")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(meses)
ax.set_xlabel("Mês", fontsize=11)
ax.set_ylim(400, 900)
ax.set_ylabel("ADR mediano (R$)")
ax.set_title("Sazonalidade do preço da diária por bairro — Itapema/SC (jan-abr/2025)", pad=14, color=NAVY)
ax.annotate("Janela de dados: jan-abr/2025", xy=(0.5, 0.95), xycoords="axes fraction",
            ha="center", fontsize=9, color=CINZA)
ax.legend(title="Bairro", frameon=True, facecolor="white", edgecolor="#D5DCE8")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(True, axis="y", alpha=0.3)
salvar(fig, "grafico6_sazonalidade.png")

# ------------------------- RESUMO -------------------------
print("\n" + "=" * 80)
print("DETALHES PARA O RELATORIO (ADR/PRECO/n por combo)")
print("=" * 80)
det = {}
for bairro, perf_a in combos:
    sub = analise[analise["perfil"] == perf_a]
    if bairro:
        sub = sub[sub["suburb_norm"] == bairro]
    det[f"{perf_a} ({bairro or 'geral'})"] = {
        "adr_med": sub["adr"].median(),
        "preco_med": sub["preco_mediana"].median(),
        "n": len(sub),
        "roi_60_mediano": sub["roi_60"].median(),
    }
print(pd.DataFrame(det).T.to_string())