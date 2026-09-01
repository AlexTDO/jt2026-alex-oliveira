# -*- coding: utf-8 -*-
"""Analise da tese dos compactos no Centro - prepara dados, calcula ROI, compara perfis."""
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

DATA = "data"


def norm_suburb(s):
    if pd.isna(s):
        return "NAO_INFORMADO"
    s = str(s).strip().lower()
    s = s.replace("são", "sao").replace("ã", "a").replace("á", "a").replace("é", "e")
    return s.title()


def load(name):
    return pd.read_csv(f"{DATA}/{name}", encoding="utf-8-sig", low_memory=False)


details = load("Details_Itapema.csv")
hosts = load("Hosts_ids_Itapema.csv")
mesh = load("Mesh_Ids_Data_Itapema.csv")
prices = load("Price_AV_Itapema.csv")
vivareal = load("VivaReal_Itapema.csv")

# ---------- 1. Preparacao: localizacao via Mesh + normalizar bairros ----------
mesh["suburb_norm"] = mesh["suburb"].map(norm_suburb)
details = details.merge(
    mesh[["airbnb_listing_id", "latitude", "longitude", "suburb_norm"]],
    on="airbnb_listing_id", how="left")

# ---------- 2. Precos: metricas por listing ----------
print("=== PRICE_AV: limpeza ===")
print(f"linhas: {len(prices)} | listings unicos: {prices['airbnb_listing_id'].nunique()}")
print("preco > 5000:", (prices["price"] > 5000).sum())
prices = prices[prices["price"] <= 5000]
print(f"apos remover > 5000: linhas {len(prices)} | listings unicos {prices['airbnb_listing_id'].nunique()}")

prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
prices["month"] = prices["date"].dt.month

# Metricas por listing
p_list = (prices.groupby("airbnb_listing_id")
          .agg(noites=("date", "nunique"),
               receita_bruta=("price", "sum"),
               adr=("price", "mean"),
               adr_mediana=("price", "median"),
               data_min=("date", "min"),
               data_max=("date", "max"))
          .reset_index())
p_list["receita_anual_potencial"] = p_list["adr"] * 365  # ocupacao 100%
p_list["receita_anual_60"] = p_list["adr"] * 365 * 0.60  # ocupacao 60%

# ---------- 3. Merge com Details (perfil/tipologia) e Hosts ----------
# Hosts tem owner_id duplicados (4.440 linhas x 3.057 chaves) -> deduplicar antes do merge
hosts = hosts.drop_duplicates(subset="owner_id", keep="first")
perfil = details[["airbnb_listing_id", "number_of_bedrooms", "number_of_bathrooms",
                  "number_of_guests", "listing_type", "owner_id", "suburb_norm"]].copy()

def bucket_bedrooms(n):
    if n <= 1:
        return "Studio/1q"
    if n == 2:
        return "2q"
    if n >= 3:
        return "3q+"

perfil["perfil"] = perfil["number_of_bedrooms"].map(bucket_bedrooms)

analise = perfil.merge(p_list, on="airbnb_listing_id", how="inner")
analise = analise.merge(hosts[["owner_id", "is_superhost"]], on="owner_id", how="left")
print(f"\nlistings com preco + perfil + bairro: {len(analise)}")

# ---------- 4. VivaReal: custo de compra por bairro x perfil ----------
vivareal["suburb_norm"] = vivareal["suburb"].map(norm_suburb)
vivareal["perfil"] = vivareal["bedrooms"].map(bucket_bedrooms)
# apenas apartamentos, apenas venda
vr = vivareal[(vivareal["listing_type"] == "apartamento") & (vivareal["sale_price"] >= 50000)]
vr = vr[vr["usable_area"] <= 1500]  # remove area suja
print(f"\nVivaReal (apartamentos p/ venda, area ok): {len(vr)} anúncios")

compra = (vr.groupby(["suburb_norm", "perfil"])["sale_price"]
          .agg(["median", "mean", "count"])
          .rename(columns={"median": "preco_mediana", "mean": "preco_media", "count": "n_ofertas"})
          .reset_index())

print("\n=== CUSTO DE COMPRA (mediana R$, VivaReal) por bairro x perfil ===")
print(compra[compra["suburb_norm"].isin(["Centro", "Meia Praia"])].to_string(index=False))

# ---------- 5. Receita por bairro x perfil ----------
receita = (analise.groupby(["suburb_norm", "perfil"])
           .agg(anuncios=("airbnb_listing_id", "nunique"),
                noites_mediana=("noites", "median"),
                adr=("adr", "median"),
                receita_bruta_potencial=("receita_anual_potencial", "median"),
                receita_anual_60=("receita_anual_60", "median"))
           .rename(columns={"adr": "adr_mediana"})
           .reset_index())

print("\n=== RECEITA por bairro x perfil (mediana por listing) ===")
print(receita[receita["suburb_norm"].isin(["Centro", "Meia Praia"])].to_string(index=False))

# ---------- 6. Tabela de ROI ----------
roi = receita.merge(compra, on=["suburb_norm", "perfil"], how="left")
roi["roi_potencial"] = roi["receita_bruta_potencial"] / roi["preco_mediana"] * 100
roi["roi_60"] = roi["receita_anual_60"] / roi["preco_mediana"] * 100
roi["payback_60_anos"] = roi["preco_mediana"] / roi["receita_anual_60"]

print("\n=== TABELA COMPARATIVA (Centro e Meia Praia) ===")
cols = ["suburb_norm", "perfil", "anuncios", "noites_mediana", "adr_mediana",
        "receita_bruta_potencial", "preco_mediana", "n_ofertas", "roi_potencial",
        "receita_anual_60", "roi_60", "payback_60_anos"]
print(roi[roi["suburb_norm"].isin(["Centro", "Meia Praia"])][cols].to_string(index=False))

# ---------- 7. Visao geral de todos os bairros (ranking) ----------
print("\n=== RANKING GERAL (todos bairros com dados, ROI potencial) ===")
geral = roi.dropna(subset=["preco_mediana"]).sort_values("roi_potencial", ascending=False)
print(geral[cols].to_string(index=False))

# ---------- 8. Estatisticas de apoio ----------
print("\n=== APOIO: quartos no Airbnb (Details) - bairro centrais ===")
print(analise[analise["suburb_norm"].isin(["Centro", "Meia Praia"])]
      .groupby(["suburb_norm", "perfil"])
      .size().unstack(fill_value=0).to_string())

print("\n=== APOIO: imoveis venda por quartos (VivaReal, Centro & Meia Praia) ===")
print(vr[vr["suburb_norm"].isin(["Centro", "Meia Praia"])]
      .groupby(["suburb_norm", "perfil"])["sale_price"]
      .agg(["median", "count"]).to_string())

print("\n=== APOIO: adr por mes (sazonalidade) ===")
print(prices.merge(details[["airbnb_listing_id", "suburb_norm"]], on="airbnb_listing_id", how="left")
      .groupby(["suburb_norm", "month"])["price"].median().unstack().loc[["Centro", "Meia Praia"]].to_string())

# salvar bases preparadas
analise.to_csv("metricas/data_preparada_airbnb.csv", index=False)
roi.to_csv("metricas/roi_comparativo.csv", index=False)
print("\nsalvo: data_preparada_airbnb.csv, roi_comparativo.csv")