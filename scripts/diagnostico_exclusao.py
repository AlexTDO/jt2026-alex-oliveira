# -*- coding: utf-8 -*-
"""Diagnostico: por que 999 anúncios com preco viraram 972 na analise de ROI.

Reproduz o pipeline de analise_bi_graficos.py e identifica, um a um, os anúncios
que ficaram sem preco de compra (VivaReal) e a causa raiz.
"""
import pandas as pd
import numpy as np

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)
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


def bucket_bedrooms(n):
    if n <= 1:
        return "Studio/1q"
    if n == 2:
        return "2q"
    return "3q+"


print("1) Carregando dados...")
details = load("Details_Itapema.csv")
mesh = load("Mesh_Ids_Data_Itapema.csv")
prices = load("Price_AV_Itapema.csv")
vivareal = load("VivaReal_Itapema.csv")

# ------------------------- PIPELINE (identico ao bi) -------------------------
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

perfil = details[["airbnb_listing_id", "number_of_bedrooms", "suburb_norm"]].copy()
perfil["perfil"] = perfil["number_of_bedrooms"].map(bucket_bedrooms)

analise = perfil.merge(p_list, on="airbnb_listing_id", how="inner")

# VivaReal: custo de compra por bairro x perfil
vivareal["suburb_norm"] = vivareal["suburb"].map(norm_suburb)
vivareal["perfil"] = vivareal["bedrooms"].map(bucket_bedrooms)
print(f"\n2) VivaReal bruto: {len(vivareal)} anúncios | uniquo listing_id: {vivareal['listing_id'].nunique()}")

# Filtros do VivaReal no pipeline
vr_filtrado = vivareal[(vivareal["listing_type"] == "apartamento")
                       & (vivareal["sale_price"] >= 50000)
                       & (vivareal["usable_area"] <= 1500)]
print(f"   Apos filtros (apartamento, preco>=50k, area<=1500): {len(vr_filtrado)} anúncios")

compra = (vr_filtrado.groupby(["suburb_norm", "perfil"])["sale_price"]
          .agg(preco_mediana="median", n_ofertas="count").reset_index())

# ------------------------- DIAGNOSTICO -------------------------
antes = len(analise)
analise = analise.merge(compra, on=["suburb_norm", "perfil"], how="left")
tem_preco = analise["preco_mediana"].notna()
sem_preco = analise[~tem_preco]
depois = len(analise[tem_preco])

print(f"\n3) DIAGNOSTICO")
print(f"   Anúncios Airbnb com preco (outliers removidos):    {antes}")
print(f"   Com preco de compra correspondente (VivaReal):     {depois}")
print(f"   SEM preco de compra (excluidos):                   {len(sem_preco)}")

print(f"\n4) Nº de combinações bairro×perfil no VivaReal: {len(compra)}")

# Tabela: combinações dos EXCLUÍDOS (bairro x perfil) e o que aconteceu
print("\n5) ANÚNCIOS EXCLUÍDOS - detalhe por bairro x perfil")
agg_sem = (sem_preco.groupby(["suburb_norm", "perfil"])
           .agg(query_anuncios=("airbnb_listing_id", "count"))
           .reset_index())

# Junta: ofertas no VivaReal vivo? antes do filtro de listing_type?
all_vr_by_key = (vivareal.groupby(["suburb_norm", "perfil"])
                 .agg(ofertas_brutas=("listing_id", "count"),
                      tem_apartamento=("listing_type", lambda s: (s == "apartamento").any()))
                 .reset_index())

diagnostico = agg_sem.merge(compra, on=["suburb_norm", "perfil"], how="left")
diagnostico = diagnostico.merge(all_vr_by_key, on=["suburb_norm", "perfil"], how="left")
print(f"\n{'Bairro':<26}{'Perfil':<11}{'Excluidos':>10}{'Ofertas_VR':>12}{'Filtradas?':>12}")
for _, r in diagnostico.sort_values("query_anuncios", ascending=False).iterrows():
    n_an = int(r["query_anuncios"])
    n_off = r.get("ofertas_brutas", 0)
    n_off = 0 if pd.isna(n_off) else int(n_off)
    tem_ap = r.get("tem_apartamento", False)
    tem_ap = False if tem_ap is None else bool(tem_ap)
    print(f"{r['suburb_norm']:<26}{r['perfil']:<11}{n_an:>10}{n_off:>12}{'sim' if tem_ap else 'nao':>12}")

# Causas raiz: quantos excluidos estao em chaves sem NENHUMA oferta?
print("\n6) CAUSAS")
chaves_sem_oferta = set()
for _, r in sem_preco.iterrows():
    chave = (r["suburb_norm"], r["perfil"])
    oferta = compra[(compra["suburb_norm"] == chave[0]) & (compra["perfil"] == chave[1])]
    if len(oferta) == 0:
        chaves_sem_oferta.add(chave)

# Quantos bairros (sem oferta) existem no Airbnb? bairros que nao tem contraparte na venda?
bairros_airbnb = set(analise[~tem_preco]["suburb_norm"])
bairros_vivareal = set(vivareal["suburb_norm"])
print(f"   Bairros no Airbnb sem preco de compra: {sorted(bairros_airbnb)}")
print(f"   Bairros que existem no VivaReal: {len(bairros_vivareal)}")
bairros_nos_vr = sorted(bairros_airbnb - bairros_vivareal)
bairros_no_vr = sorted(bairros_airbnb & bairros_vivareal)
print(f"   Bairros EXCLUSIVOS do Airbnb (sem nenhuma oferta VivaReal): {bairros_nos_vr}")
print(f"   Bairros com presenca em ambos: {bairros_no_vr}")

print("\n7) DETALHE das chaves sem oferta e o que havia no Airbnb:")
det = sem_preco.groupby(["suburb_norm", "perfil"]).agg(n=("airbnb_listing_id", "count"))
for (bairro, perf), r in det.iterrows():
    # ofertas para essa chave no VivaReal (todas, sem filtro)
    oferta_bruta = all_vr_by_key[(all_vr_by_key["suburb_norm"] == bairro)
                                 & (all_vr_by_key["perfil"] == perf)]
    nota = ""
    if len(oferta_bruta) == 0:
        nota = "-> 0 ofertas de venda para essa chave"
    else:
        n_ofertas = int(oferta_bruta["ofertas_brutas"].iloc[0])
        tem_ap = bool(oferta_bruta["tem_apartamento"].iloc[0])
        if not tem_ap:
            nota = f"-> {n_ofertas} ofertas, nenhuma do tipo 'apartamento'"
        else:
            # tem apartamento mas excluido pelo filtro de preco ou area?
            vr_chave = vr_filtrado[(vr_filtrado["suburb_norm"] == bairro)
                                   & (vr_filtrado["perfil"] == perf)]
            sem_filtro = vivareal[(vivareal["suburb_norm"] == bairro)
                                  & (vivareal["perfil"] == perf)]
            nota = (f"-> {n_ofertas} ofertas; filtro de preco/area removeu "
                    f"{len(sem_filtro) - len(vr_chave)} delas -> restaram {len(vr_chave)}")
    print(f"   {bairro:<26}{perf:<11}n_excluidos={int(r['n']):<4} {nota}")

# Verificacao: e um bairro sem oferta nada, ou so perfil?
print("\n8) TOTAL: soma contagens da tabela acima deve bater com 27")
print(f"   Excluidos: {len(sem_preco)}")

# ------------------------- VIÉS? -------------------------
print("\n9) ANÁLISE DE VIÉS: comparar ADR/tipologia de incluidos vs excluidos")
incl = analise[tem_preco]
for perfil in ["Studio/1q", "2q", "3q+"]:
    s_inc = incl[incl["perfil"] == perfil]["adr"].median()
    s_exc = sem_preco[sem_preco["perfil"] == perfil]["adr"].median() if len(sem_preco[sem_preco["perfil"] == perfil]) else float("nan")
    n_inc = len(incl[incl["perfil"] == perfil])
    n_exc = len(sem_preco[sem_preco["perfil"] == perfil])
    print(f"   {perfil:<10} incluidos n={n_inc:<4} ADR med={s_inc:,.2f}  |  excluidos n={n_exc:<4} ADR med={s_exc:,.2f}")

print("\n10) Distribuicao por bairro: incluidos vs excluidos")
print(incl["suburb_norm"].value_counts().head(8).to_string())
print("Excluidos:")
print(sem_preco["suburb_norm"].value_counts().to_string())