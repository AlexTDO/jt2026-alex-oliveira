# -*- coding: utf-8 -*-
"""Mapeamento de relacionamentos entre arquivos + primeiros insights."""
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

DATA = "data"
frames = {}
for key, fname in {
    "details": "Details_Itapema.csv",
    "hosts": "Hosts_ids_Itapema.csv",
    "mesh": "Mesh_Ids_Data_Itapema.csv",
    "prices": "Price_AV_Itapema.csv",
    "vivareal": "VivaReal_Itapema.csv",
}.items():
    frames[key] = pd.read_csv(f"{DATA}/{fname}", encoding="utf-8-sig", low_memory=False)

d = frames["details"]
h = frames["hosts"]
m = frames["mesh"]
p = frames["prices"]
v = frames["vivareal"]

print("### RELACIONAMENTOS (JOINS) ###")
print("-" * 80)

# Details <-> Mesh
joins = {
    "Details vs Mesh (airbnb_listing_id)": (d, m),
    "Details vs Hosts (owner_id)": (d, h),
    "Details vs Prices (airbnb_listing_id)": (d, p),
}
for label, (a, b) in joins.items():
    key = "airbnb_listing_id" if "listing" in label.split(" vs ")[1] and "owner" not in label.split(" vs ")[1] else ("owner_id" if "Hosts" in label else "airbnb_listing_id")
    ids_a = set(a[key].unique())
    ids_b = set(b[key].unique())
    inter = ids_a & ids_b
    in_a_not_b = ids_a - ids_b
    in_b_not_a = ids_b - ids_a
    print(f"{label}:")
    print(f"  key={key}  | A={len(ids_a)} unicos | B={len(ids_b)} unicos")
    print(f"  na interseccao: {len(inter)}  | somente em A: {len(in_a_not_b)} | somente em B: {len(in_b_not_a)}")
    print(f"  % de A com correspondencia em B: {100*len(inter)/len(ids_a):.2f}%")
    print()

# Prices coverage per listing
print("Price_AV coverage:")
print(f"  linhas: {len(p)} | listings unicos: {p['airbnb_listing_id'].nunique()}")
p["date"] = pd.to_datetime(p["date"], errors="coerce")
pp = p.groupby("airbnb_listing_id").agg(linhas=("price", "count"), data_min=("date", "min"), data_max=("date", "max")).reset_index()
print(f"  datas cobertas por listing: min linhas={pp['linhas'].min()}, mediana={pp['linhas'].median():.0f}, max={pp['linhas'].max()}")
print(f"  range de datas global: {p['date'].min()} a {p['date'].max()}")
print()
print(f"  listings detalhes sem nenhum preco: {len(set(d['airbnb_listing_id'])-set(p['airbnb_listing_id']))}")
print(f"  precos de listings fora de details (vir/conta de captura): {len(set(p['airbnb_listing_id'])-set(d['airbnb_listing_id']))}")
print()

# Details lat/long zero?
print("Details lat/long == 0 (sem coordenadas):")
print(f"  lat==0: {(d['latitude']==0).sum()} | lon==0: {(d['longitude']==0).sum()}")
print(f"  Mesh lat/long validas: {(m['latitude']!=0).sum()}")
print()

print("### INSIGHTS ###")
print("-" * 80)
print("listing_type (Details):")
print(d["listing_type"].value_counts(dropna=False).to_string())
print()
print("suburb (Mesh):")
print(m["suburb"].value_counts(dropna=False).head(15).to_string())
print()
print("quartos (Details, number_of_bedrooms):")
print(d["number_of_bedrooms"].value_counts().sort_index().to_string())
print()
print("is_new_listing:")
print(d["is_new_listing"].value_counts(dropna=False).to_string())
print()
print("is_professional:")
print(d["is_professional"].value_counts(dropna=False).head(8).to_string())
print()
print("star_rating == 0 (sem avaliacao):", (d["star_rating"] == 0).sum(), "/", len(d))

# Prices agreggate per listing
pl = p.groupby("airbnb_listing_id")["price"].agg(["mean", "median", "min", "max", "count"])
print()
print("Preco av noite por listing (R$):")
print(pl[["mean", "median", "min", "max"]].describe().to_string())
print()

# VivaReal insights
print("VivaReal property_type:")
print(v["property_type"].value_counts(dropna=False).head(10).to_string())
print()
print("VivaReal listing_type:")
print(v["listing_type"].value_counts(dropna=False).to_string())
print()
print("VivaReal suburb:")
print(v["suburb"].value_counts(dropna=False).head(15).to_string())
print()
print("VivaReal sale_price outliers (>10M):", (v["sale_price"] > 10_000_000).sum())
print("VivaReal usable_area outliers (>1500 m2):", (v["usable_area"] > 1500).sum())
print()
print("VivaReal duplicated rows:", v.duplicated().sum())
print("VivaReal duplicates por listing_id:", v["listing_id"].duplicated().sum())

# Hosts insights
print()
print("Superhost share:", round(100 * h["is_superhost"].mean(), 2), "%")
print("Hosts com 0 reviews:", (h["number_of_reviews_host"] == 0).sum(), "de", len(h))
print("Owner_ids q nao aparecem em Details:", len(set(h["owner_id"]) - set(d["owner_id"])))