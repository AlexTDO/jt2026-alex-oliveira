# -*- coding: utf-8 -*-
"""Exploracao inicial dos dados de Itapema (Seazone Hackathon)."""
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

DATA = "data"
FILES = {
    "details": "Details_Itapema.csv",
    "hosts": "Hosts_ids_Itapema.csv",
    "mesh": "Mesh_Ids_Data_Itapema.csv",
    "prices": "Price_AV_Itapema.csv",
    "vivareal": "VivaReal_Itapema.csv",
}

# Detect encoding per file
def read_csv(name):
    for enc in ("utf-8-sig", "latin-1", "utf-8"):
        try:
            df = pd.read_csv(f"{DATA}/{name}", encoding=enc, low_memory=False)
            return df, enc
        except UnicodeDecodeError:
            continue
    return pd.read_csv(f"{DATA}/{name}", low_memory=False), "default"

frames = {}
encodings = {}
for key, fname in FILES.items():
    df, enc = read_csv(fname)
    frames[key] = df
    encodings[key] = enc
    print("=" * 90)
    print(f"### FILE: {fname}  (encoding={enc})  shape={df.shape}")
    print("-" * 90)
    print("COLUMNS:", df.columns.tolist())
    print()
    print("DTYPES:")
    print(df.dtypes)
    print()
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    print("MISSING (>0):")
    if len(missing) == 0:
        print("  (none)")
    else:
        print(missing)
    print()
    print("HEAD:")
    print(df.head().to_string())
    print()
    print("DESCRIBE (numericas):")
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        print(df[num_cols].describe().to_string())
    else:
        print("  (no numeric columns)")
    print()
    print("DUPLICATED:", df.duplicated().sum())
    print()

# Index column checks (first col looks like row number?)
print("=" * 90)
print("PRIMEIRA COLUNA == index implícito (0..n-1)?")
for key, df in frames.items():
    c0 = df.columns[0]
    match = (df[c0].astype(str) == np.arange(len(df)).astype(str)).all()
    print(f"  {key}: col '{c0}' -> index-like: {match}")