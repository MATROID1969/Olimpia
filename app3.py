#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# app.py
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Olimpiai klaszterek", layout="wide")


# -------------------------------------------------
# 1) Adatfeldolgozás
# -------------------------------------------------
@st.cache_data
def load_and_prepare_data(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)

    country_summary = (
        df.groupby("Country", as_index=False)
          .agg({
              "Gold": "sum",
              "Silver": "sum",
              "Bronze": "sum"
          })
    )

    country_summary["Total_Medals"] = (
        country_summary["Gold"] +
        country_summary["Silver"] +
        country_summary["Bronze"]
    )

    denom = country_summary["Total_Medals"].replace(0, np.nan)
    country_summary["Gold_Ratio"] = (
        country_summary["Gold"] / denom
    ).fillna(0).round(2)

    return country_summary


# -------------------------------------------------
# 2) K-means előszámítás
# -------------------------------------------------
@st.cache_data
def precompute_kmeans(country_summary, k_list=(3,4,5,6,7,8)):

    X = country_summary[["Total_Medals", "Gold_Ratio"]]
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    out = country_summary.copy()
    centroid_rows = []

    for k in k_list:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        out[f"Cluster_{k}"] = labels

        centroids = scaler.inverse_transform(kmeans.cluster_centers_)
        for cluster_id in range(k):
            centroid_rows.append({
                "K": k,
                "Cluster": cluster_id,
                "Total_Medals": float(centroids[cluster_id, 0]),
                "Gold_Ratio": float(centroids[cluster_id, 1])
            })

    centroids_df = pd.DataFrame(centroid_rows)
    return out, centroids_df


# -------------------------------------------------
# 3) Segédfüggvények
# -------------------------------------------------
def get_colors(k):
    cmap = plt.get_cmap("tab10")
    return [cmap(i) for i in range(k)]


def get_cluster_names(k):
    if k == 5:
        return {
            0: "Pechesek",
            1: "Átlagteljesítők",
            2: "(Érem) nagyhatalmak",
            3: "Arany-specialisták",
            4: "Siker-orientáltak"
        }
    return {i: f"Klaszter {i}" for i in range(k)}


def highlight_hungary(row):
    country_value = str(row["Country"])
    if "Magyarország" in country_value:
        return ["color: red"] * len(row)
    return [""] * len(row)


# -------------------------------------------------
# 4) App fő rész
# -------------------------------------------------
st.title("Olimpiai országok K-means klaszterezése")

file_path = "olimpic_upload.xlsx"

country_summary = load_and_prepare_data(file_path)
country_summary_k, centroids_all = precompute_kmeans(country_summary)

# Fix tengelyhatárok
x_min = country_summary_k["Total_Medals"].min()
y_min = country_summary_k["Gold_Ratio"].min()

x_max = country_summary_k["Total_Medals"].max()
y_max = country_summary_k["Gold_Ratio"].max()

x_pad = 0.05 * (x_max - x_min)
y_pad = 0.05 * (y_max - y_min)

xlim = (x_min - x_pad, x_max + x_pad)
ylim = (y_min - y_pad, y_max + y_pad)

# -----------------------------
# Widgetek (felül)
# -----------------------------
w1, w2 = st.columns(2)

with w1:
    selected_k = st.selectbox("Klaszterszám", [3,4,5,6,7,8], index=2)

with w2:
    view_mode = st.selectbox("Nézet", ["full", "centroid"])

cluster_col = f"Cluster_{selected_k}"
viz_df = country_summary_k.copy()
viz_df["Cluster"] = viz_df[cluster_col].astype(int)

# -----------------------------
# Középső layout (azonos méret)
# -----------------------------
col_plot, col_table = st.columns(2)

# =============================
# PLOT
# =============================
with col_plot:
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = get_colors(selected_k)

    if view_mode == "full":
        for cid in range(selected_k):
            d = viz_df[viz_df["Cluster"] == cid]
            ax.scatter(
                d["Total_Medals"],
                d["Gold_Ratio"],
                color=colors[cid],
                s=30,
                alpha=0.35
            )

    else:  # centroid nézet
        names = get_cluster_names(selected_k)
        centroids_df = centroids_all[centroids_all["K"] == selected_k]

        x_offset = 0.02 * (xlim[1] - xlim[0])
        y_offset = 0.02 * (ylim[1] - ylim[0])

        for cid in range(selected_k):
            row = centroids_df[centroids_df["Cluster"] == cid].iloc[0]
            cx, cy = row["Total_Medals"], row["Gold_Ratio"]

            d = viz_df[viz_df["Cluster"] == cid]
            n = len(d)
            avg_gold = d["Gold"].mean()
            avg_ratio = d["Gold_Ratio"].mean()

            cluster_size = len(d)
            size_scaled = 60 + (cluster_size ** 0.5) * 25
            # méretezés (skálázva, hogy ne legyen túl kicsi vagy túl nagy)
            size_scaled = 40 + cluster_size * 8
            ax.scatter(cx, cy,
                       color=colors[cid],
                       s=size_scaled,
                       edgecolors="black")
            

            label = (
                f"{names[cid]}\n"
                f"N={n}\n"
                f"Avg Gold={avg_gold:.1f}\n"
                f"Avg Ratio={avg_ratio:.2f}"
            )

            ax.text(cx + x_offset,
                    cy + y_offset,
                    label,
                    fontsize=9,
                    color=colors[cid])

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel("Total Medals")
    ax.set_ylabel("Gold Ratio")

    st.pyplot(fig, clear_figure=True)

# =============================
# TÁBLÁZAT
# =============================
with col_table:

    # ÚJ WIDGET a táblázat felett
    cluster_options = ["full"] + list(range(selected_k))
    selected_cluster_filter = st.selectbox(
        "Klaszter szűrés",
        cluster_options
    )

    table_df = viz_df[["Country", "Cluster", "Total_Medals", "Gold_Ratio"]].copy()
    table_df["Gold_Ratio"] = (table_df["Gold_Ratio"] * 100).round(1).astype(str) + " %"

    if selected_cluster_filter != "full":
        table_df = table_df[table_df["Cluster"] == selected_cluster_filter]

    table_df = table_df.sort_values(
        ["Cluster", "Total_Medals"],
        ascending=[True, False]
    )

    styled_table = table_df.style.apply(highlight_hungary, axis=1)

    st.dataframe(
        styled_table,
        use_container_width=True,
        height=500   # közel azonos vizuális magasság
    )


# In[ ]:




