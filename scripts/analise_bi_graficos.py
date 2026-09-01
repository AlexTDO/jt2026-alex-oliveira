# -*- coding: utf-8 -*-
"""BI Analysis - Itapema/SC. Gera 5 graficos profissionais em alta resolução."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

DATA = "data"
OUT = "graficos"
os.makedirs(OUT, exist_ok=True)

# Seazone brand palette
NAVY = "#00143D"
AZUL = "#0055FF"
CORAL = "#FC6058"
AZUL_CLARO = "#7DA8FF"
CINZA = "#8A97AE"
VERDE = "#2E8B57"
PALETA = [AZUL, CORAL, VERDE, "#8E6FC8", "#2C9FA3", NAVY]

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


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(f"{OUT}/{nome}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  salvou {OUT}/{nome}")


# ------------------------- PREPARAÇÃO -------------------------
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
p_list = (prices.groupby("airbnb_listing_id")
          .agg(noites=("date", "nunique"),
               receita_bruta=("price", "sum"),
               adr=("price", "mean"))
          .reset_index())
p_list["receita_anual_potencial"] = p_list["adr"] * 365
p_list["receita_anual_60"] = p_list["adr"] * 365 * 0.60

hosts = hosts.drop_duplicates(subset="owner_id", keep="first")

perfil = details[[
    "airbnb_listing_id", "number_of_bedrooms", "number_of_bathrooms",
    "number_of_beds", "number_of_guests", "cleaning_fee", "url", "ad_name",
    "ad_description", "amenities", "number_of_reviews", "star_rating",
    "picture_count", "listing_type", "owner_id", "suburb_norm",
    "guest_satisfaction_overall", "accuracy_rating", "checkin_rating",
    "cleanliness_rating", "communication_rating", "location_rating",
    "value_rating", "is_guest_favorite", "can_instant_book",
]].copy()
perfil["perfil"] = perfil["number_of_bedrooms"].map(bucket_bedrooms)

analise = perfil.merge(p_list, on="airbnb_listing_id", how="inner")
analise = analise.merge(hosts[["owner_id", "is_superhost", "years_host",
                               "months_host", "number_of_reviews_host"]],
                        on="owner_id", how="left")
print(f"Listings com preço + perfil + bairro: {len(analise)}")

# VivaReal: custo de compra por bairro x perfil
vivareal["suburb_norm"] = vivareal["suburb"].map(norm_suburb)
vivareal["perfil"] = vivareal["bedrooms"].map(bucket_bedrooms)
vr = vivareal[(vivareal["listing_type"] == "apartamento")
              & (vivareal["sale_price"] >= 50000)
              & (vivareal["usable_area"] <= 1500)]
compra = (vr.groupby(["suburb_norm", "perfil"])["sale_price"]
          .agg(preco_mediana="median", n_ofertas="count").reset_index())

# Por-listing: atribui preço de compra mediano do seu bairro x perfil
analise = analise.merge(compra, on=["suburb_norm", "perfil"], how="left")
analise["roi_potencial"] = analise["receita_anual_potencial"] / analise["preco_mediana"] * 100
analise["roi_60"] = analise["receita_anual_60"] / analise["preco_mediana"] * 100
analise["payback_60"] = analise["preco_mediana"] / analise["receita_anual_60"]
analise["is_superhost"] = analise["is_superhost"].fillna(False).astype(int)
analise["is_guest_favorite"] = analise["is_guest_favorite"].astype(int)

# ---- Dados de apoio para o relatório (métricas por perfil/bairro) ----
print("\n=== METRICAS POR PERFIL (mediana, todos bairros) ===")
perf_res = (analise.dropna(subset=["preco_mediana"])
            .groupby("perfil").agg(
                anuncios=("airbnb_listing_id", "count"),
                adr=("adr", "median"),
                receita_annual_60=("receita_anual_60", "median"),
                preco=("preco_mediana", "median"),
                roi=("roi_60", "median"),
                payback=("payback_60", "median"))
            .reindex(["Studio/1q", "2q", "3q+"]))
print(perf_res.to_string())

print("\n=== METRICAS POR BAIRRO (mediana, bairros com >=4 listings) ===")
bairro_res = (analise.dropna(subset=["preco_mediana"])
              .groupby("suburb_norm").agg(
                  anuncios=("airbnb_listing_id", "count"),
                  adr=("adr", "median"),
                  roi=("roi_60", "median"),
                  payback=("payback_60", "median"))
              .query("anuncios >= 4")
              .sort_values("roi", ascending=False))
bairro_res["participacao"] = 100 * bairro_res["anuncios"] / analise["airbnb_listing_id"].nunique()
print(bairro_res.to_string())

# ------------------------- GRÁFICO 1: ROI por Perfil -------------------------
print("\nGráfico 1 - ROI por perfil")
fig, ax = plt.subplots(figsize=(8, 5))
lp = analise.dropna(subset=["preco_mediana"])
order = ["Studio/1q", "2q", "3q+"]
med = lp.groupby("perfil")["roi_60"].median().reindex(order)
med_pay = lp.groupby("perfil")["payback_60"].median().reindex(order)
n = lp.groupby("perfil")["airbnb_listing_id"].count().reindex(order)

cores = [PALETA[0], PALETA[1], CINZA]
bars = ax.bar(range(len(order)), med.values, color=cores, width=0.6, edgecolor=NAVY, linewidth=0.6, zorder=3)
for i, (v, p, cnt) in enumerate(zip(med.values, med_pay.values, n.values)):
    ax.text(i, v + 0.15, f"{v:.1f}%", ha="center", va="bottom", fontsize=12, fontweight="bold", color=NAVY)
    ax.text(i, -1.2, f"payback {p:.1f} anos", ha="center", fontsize=9, color=CINZA)
    ax.text(i, v - 1.4, f"n={cnt}", ha="center", fontsize=9, color="white", fontweight="bold")
ax.set_xticks(range(len(order)))
ax.set_xticklabels(order)
ax.set_ylabel("ROI anual (% sobre preço de compra)")
ax.set_title("ROI anual por perfil de imóvel (ocupação 60%) — Itapema/SC", pad=14, color=NAVY)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, med.max() * 1.35)
ax.spines[["top", "right"]].set_visible(False)
salvar(fig, "grafico1_roi_perfil.png")

# ------------------------- GRÁFICO 2: ROI por Bairro -------------------------
print("Gráfico 2 - ROI por bairro")
fig, ax = plt.subplots(figsize=(8.5, 6))
br = bairro_res.head(8).sort_values("roi")
cores_b = [AZUL if i >= len(br) - 3 else CINZA for i in range(len(br))]
bars = ax.barh(br.index, br["roi"], color=cores_b, edgecolor=NAVY, linewidth=0.5, zorder=3)
for bar, v, a in zip(bars, br["roi"], br["adr"]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            f"{v:.1f}%  (ADR R${a:,.0f})", va="center", fontsize=10, color=NAVY, fontweight="bold")
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlabel("ROI anual (ocupação 60%)")
ax.set_title("ROI por bairro — Itapema/SC (bairros com ≥4 anúncios precificados)", pad=14, color=NAVY)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlim(0, br["roi"].max() * 1.45)
salvar(fig, "grafico2_roi_bairro.png")

# ------------------------- GRÁFICO 3: Correlações -------------------------
print("Gráfico 3 - Correlações com ADR")
feat_corr = {
    "number_of_beds": "Nº de camas",
    "number_of_guests": "Capacidade (hóspedes)",
    "number_of_bathrooms": "Nº de banheiros",
    "number_of_bedrooms": "Nº de quartos",
    "cleaning_fee": "Taxa de limpeza (R$)",
    "picture_count": "Nº de fotos",
    "number_of_reviews": "Nº de reviews",
    "star_rating": "Nota média",
    "guest_satisfaction_overall": "Satisfação geral",
    "location_rating": "Nota localização",
    "value_rating": "Nota custo-benefício",
    "years_host": "Anos como host",
    "number_of_reviews_host": "Reviews do host",
    "is_superhost": "Superhost",
    "is_guest_favorite": "Guest favorite",
}
corr_df = analise[list(feat_corr.keys()) + ["adr"]].copy()
corr = corr_df.corr(method="spearman")["adr"].drop("adr").sort_values()
fig, ax = plt.subplots(figsize=(8.5, 6.5))
labels = [feat_corr[c] for c in corr.index]
cores_c = [AZUL if v < 0 else CORAL for v in corr.values]
bars = ax.barh(range(len(corr)), corr.values, color=cores_c, edgecolor=NAVY, linewidth=0.4, zorder=3)
ax.set_yticks(range(len(corr)))
ax.set_yticklabels(labels)
ax.axvline(0, color=NAVY, linewidth=1)
for bar, v in zip(bars, corr.values):
    ax.text(bar.get_width() + (0.01 if v >= 0 else -0.01),
            bar.get_y() + bar.get_height() / 2,
            f"{v:+.2f}", va="center", fontsize=10,
            ha="left" if v >= 0 else "right", color=NAVY, fontweight="bold")
ax.set_xlabel("Correlação de Spearman com o preço da diária (ADR)")
ax.set_title("O que explica o preço da diária? — Correlações com ADR", pad=14, color=NAVY)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlim(corr.min() - 0.15, corr.max() + 0.20)
salvar(fig, "grafico3_correlacoes_adr.png")

# ------------------------- GRÁFICO 4: Payback por perfil -------------------------
print("Gráfico 4 - Payback por perfil")
fig, ax = plt.subplots(figsize=(8, 5))
precos = lp.groupby("perfil")["preco_mediana"].median().reindex(order)
valores = med_pay.values
cores_p = [PALETA[0], PALETA[1], CINZA]
bars = ax.bar(range(len(order)), valores, color=cores_p, width=0.6, edgecolor=NAVY, linewidth=0.6, zorder=3)
for i, (v, pr) in enumerate(zip(valores, precos.values)):
    ax.text(i, v + 0.15, f"{v:.1f} anos", ha="center", va="bottom", fontsize=12, fontweight="bold", color=NAVY)
    ax.text(i, v - 0.6, f"compra R${pr/1000:,.0f}k", ha="center", fontsize=10, color="white", fontweight="bold")
ax.set_xticks(range(len(order)))
ax.set_xticklabels(order)
ax.set_ylabel("Payback (anos para pagar o imóvel com receita a 60% de ocupação)")
ax.set_title("Payback do investimento por perfil de imóvel — Itapema/SC", pad=14, color=NAVY)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, valores.max() * 1.3)
salvar(fig, "grafico4_payback_perfil.png")

# ------------------------- GRÁFICO 5: Tese compactos (4 combinações) -------------------------
print("Gráfico 5 - Comparativo 4 combinações")
fig, ax = plt.subplots(figsize=(9, 6))
alvo = analise[(analise["suburb_norm"].isin(["Centro", "Meia Praia"]))
               & (analise["perfil"].isin(["Studio/1q", "2q"]))]
tab = (alvo.groupby(["perfil", "suburb_norm"])["roi_60"].median()
       .unstack().reindex(index=["Studio/1q", "2q"], columns=["Centro", "Meia Praia"]))
rec = (alvo.groupby(["perfil", "suburb_norm"])["receita_anual_60"].median()
       .unstack().reindex(index=["Studio/1q", "2q"], columns=["Centro", "Meia Praia"]))
pre = (alvo.groupby(["perfil", "suburb_norm"])["preco_mediana"].median()
       .unstack().reindex(index=["Studio/1q", "2q"], columns=["Centro", "Meia Praia"]))

labels = ["Studio/1q", "2q"]
x = np.arange(len(labels))
w = 0.35

for i, bairro in enumerate(["Centro", "Meia Praia"]):
    vals = [tab.loc[l, bairro] for l in labels]
    recs = [rec.loc[l, bairro] for l in labels]
    prs = [pre.loc[l, bairro] for l in labels]
    bars = ax.bar(x + (i - 0.5) * w, vals, w, label=bairro,
                  color=[AZUL, PALETA[1]][i], edgecolor=NAVY, linewidth=0.6, zorder=3)
    for bar, v, r, p in zip(bars, vals, recs, prs):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.15,
                f"{v:.1f}%\nR${r/1000:,.0f}k/ano", ha="center", va="bottom",
                fontsize=9.5, color=NAVY, fontweight="bold")
        ax.text(bar.get_x() + bar.get_width() / 2, v - 0.9,
                f"compra R${p/1000:,.0f}k", ha="center", fontsize=8.5,
                color="white", fontweight="bold")
roi_3q = lp.loc[lp["perfil"] == "3q+", "roi_60"].median()
ax.axhline(roi_3q, color=VERDE, linestyle="--", linewidth=1.4)
ax.text(len(labels) - 1 + 0.65, roi_3q + 0.25, f"ROI médio 3q+ ({roi_3q:.1f}%)",
        color=VERDE, fontsize=9, ha="right")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("ROI anual (ocupação 60%)")
ax.set_title("Tese dos compactos: ROI das 4 combinações Centro × Meia Praia", pad=14, color=NAVY)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.legend(title="Bairro", frameon=True, facecolor="white", edgecolor="#D5DCE8")
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, tab.values.max() * 1.55)
salvar(fig, "grafico5_tese_compactos.png")

# ------------------------- Salvar métricas para o relatório -------------------------
perf_res.to_csv("metricas/metricas_perfil.csv", encoding="utf-8-sig")
bairro_res.to_csv("metricas/metricas_bairro.csv", encoding="utf-8-sig")
corr.to_csv("metricas/correlacoes_adr.csv", encoding="utf-8-sig")
tab_md = tab.rename_axis("perfil").reset_index()
tab_md.to_csv("metricas/tese_4combinacoes.csv", index=False, encoding="utf-8-sig")
print("\nCSVs de apoio salvos.")

print("\n=== CORRELACOES (rank) ===")
print(corr.to_string())
print("\n=== TABELA TESES ===")
print(tab.to_string())
print("\n=== RECEITA TESES ===")
print(rec.to_string())
print("\n=== PRECO TESES ===")
print(pre.to_string())