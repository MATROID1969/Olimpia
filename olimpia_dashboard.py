import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─── Oldal konfiguráció ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Olimpiai Éremstatisztikák 1996–2024",
    layout="wide",
    page_icon="🏅",
)

# ─── Földrész → IOC-kód mapping ──────────────────────────────────────────────
CONTINENT_MAP = {
    # Afrika
    "ALG": "Afrika",
    "BDI": "Afrika",
    "BOT": "Afrika",
    "BUR": "Afrika",
    "CIV": "Afrika",
    "CMR": "Afrika",
    "CPV": "Afrika",
    "EGY": "Afrika",
    "ERI": "Afrika",
    "ETH": "Afrika",
    "GAB": "Afrika",
    "GHA": "Afrika",
    "KEN": "Afrika",
    "MAR": "Afrika",
    "MOZ": "Afrika",
    "MRI": "Afrika",
    "NAM": "Afrika",
    "NGR": "Afrika",
    "NIG": "Afrika",
    "RSA": "Afrika",
    "SUD": "Afrika",
    "TOG": "Afrika",
    "TUN": "Afrika",
    "UGA": "Afrika",
    "ZAM": "Afrika",
    "ZIM": "Afrika",
    # Ázsia
    "AFG": "Ázsia",
    "BRN": "Ázsia",
    "CHN": "Ázsia",
    "HKG": "Ázsia",
    "INA": "Ázsia",
    "IND": "Ázsia",
    "IRI": "Ázsia",
    "JOR": "Ázsia",
    "JPN": "Ázsia",
    "KAZ": "Ázsia",
    "KGZ": "Ázsia",
    "KOR": "Ázsia",
    "KSA": "Ázsia",
    "KUW": "Ázsia",
    "MAS": "Ázsia",
    "MGL": "Ázsia",
    "PAK": "Ázsia",
    "PHI": "Ázsia",
    "PRK": "Ázsia",
    "QAT": "Ázsia",
    "SGP": "Ázsia",
    "SIN": "Ázsia",
    "SRI": "Ázsia",
    "SYR": "Ázsia",
    "THA": "Ázsia",
    "TJK": "Ázsia",
    "TKM": "Ázsia",
    "TPE": "Ázsia",
    "UAE": "Ázsia",
    "UZB": "Ázsia",
    "VIE": "Ázsia",
    # Európa
    "ALB": "Európa",
    "ARM": "Európa",
    "AUT": "Európa",
    "AZE": "Európa",
    "BEL": "Európa",
    "BER": "Európa",
    "BLR": "Európa",
    "BUL": "Európa",
    "CRO": "Európa",
    "CYP": "Európa",
    "CZE": "Európa",
    "DEN": "Európa",
    "ESP": "Európa",
    "EST": "Európa",
    "FIN": "Európa",
    "FRA": "Európa",
    "GBR": "Európa",
    "GEO": "Európa",
    "GER": "Európa",
    "GRE": "Európa",
    "HUN": "Európa",
    "IRL": "Európa",
    "ISL": "Európa",
    "ISR": "Európa",
    "ITA": "Európa",
    "KOS": "Európa",
    "LAT": "Európa",
    "LTU": "Európa",
    "MDA": "Európa",
    "MKD": "Európa",
    "MNE": "Európa",
    "NED": "Európa",
    "NOR": "Európa",
    "POL": "Európa",
    "POR": "Európa",
    "ROU": "Európa",
    "RUS": "Európa",
    "SCG": "Európa",
    "SLO": "Európa",
    "SMR": "Európa",
    "SRB": "Európa",
    "SUI": "Európa",
    "SVK": "Európa",
    "SWE": "Európa",
    "TUR": "Európa",
    "UKR": "Európa",
    # Észak- és Közép-Amerika
    "BAH": "Észak-Amerika",
    "BAR": "Észak-Amerika",
    "CAN": "Észak-Amerika",
    "CRC": "Észak-Amerika",
    "CUB": "Észak-Amerika",
    "DMA": "Észak-Amerika",
    "DOM": "Észak-Amerika",
    "GRN": "Észak-Amerika",
    "GUA": "Észak-Amerika",
    "JAM": "Észak-Amerika",
    "LCA": "Észak-Amerika",
    "MEX": "Észak-Amerika",
    "PAN": "Észak-Amerika",
    "PUR": "Észak-Amerika",
    "TRI": "Észak-Amerika",
    "TTO": "Észak-Amerika",
    "USA": "Észak-Amerika",
    # Dél-Amerika
    "ARG": "Dél-Amerika",
    "BRA": "Dél-Amerika",
    "CHI": "Dél-Amerika",
    "COL": "Dél-Amerika",
    "ECU": "Dél-Amerika",
    "PAR": "Dél-Amerika",
    "PER": "Dél-Amerika",
    "URU": "Dél-Amerika",
    "VEN": "Dél-Amerika",
    # Óceánia
    "AUS": "Óceánia",
    "FIJ": "Óceánia",
    "NZL": "Óceánia",
    "TGA": "Óceánia",
    # Semleges / egyéb
    "AIN": "Egyéb",
    "EOR": "Egyéb",
    "IOA": "Egyéb",
    "ROC": "Egyéb",
}

OLYMPICS_ORDER = [
    "1996 Atlanta",
    "2000 Sydney",
    "2004 Athén",
    "2008 Peking",
    "2012 London",
    "2016 Rio de Janeiro",
    "2020 Tokió",
    "2024 Párizs",
]

CONTINENT_COLORS = {
    "Európa": "#4361EE",
    "Ázsia": "#F72585",
    "Afrika": "#2DC653",
    "Észak-Amerika": "#FF9F1C",
    "Dél-Amerika": "#FFBF69",
    "Óceánia": "#00B4D8",
}

CONTINENT_CENTROIDS = {
    "Európa": {"lat": 54, "lon": 15},
    "Ázsia": {"lat": 35, "lon": 100},
    "Afrika": {"lat": 5, "lon": 22},
    "Észak-Amerika": {"lat": 48, "lon": -95},
    "Dél-Amerika": {"lat": -15, "lon": -58},
    "Óceánia": {"lat": -25, "lon": 140},
}

MEDAL_OPTIONS = {
    "Összes érem": "Total",
    "🟡 Arany": "Gold",
    "⚪ Ezüst": "Silver",
    "🟠 Bronz": "Bronze",
}

MEDAL_COLORS = {
    "Total": "#4FC3F7",
    "Gold": "#FFD700",
    "Silver": "#C0C0C0",
    "Bronze": "#CD7F32",
}


# ─── Adatok betöltése ────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel("olimpic_upload.xlsx")
    df["Code"] = df["Country"].str.extract(r"\(([A-Z]+)\)")
    df["Continent"] = df["Code"].map(CONTINENT_MAP).fillna("Egyéb")
    df["Olimpics"] = pd.Categorical(
        df["Olimpics"], categories=OLYMPICS_ORDER, ordered=True
    )
    return df


df = load_data()
df_main = df[df["Continent"] != "Egyéb"]

# ─── Session state: kijelölt földrész ─────────────────────────────────────────
if "selected_continent" not in st.session_state:
    st.session_state.selected_continent = None
if "map_key" not in st.session_state:
    st.session_state.map_key = 0

selected = st.session_state.selected_continent

# ─── Fejléc ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; padding: 0.5rem 0 0.2rem 0;">
        <h1 style="color:#FFD700; font-size:2.3rem; margin-bottom:0.1rem;">
            🏅 Olimpiai Éremstatisztikák 1996–2024
        </h1>
        <p style="color:#aaa; font-size:1.05rem; margin-top:0;">
            Kovács Gyula Picasso tréning &nbsp;·&nbsp; <a href="https://kovacsgyulacoach.hu/" target="_blank" style="color:#FFD700;">kovacsgyulacoach.hu</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ─── KPI kártyák ─────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🌍 Résztvevő ország", df_main["Country"].nunique())
k2.metric("🏅 Összes érem", f"{int(df_main['Total'].sum()):,}".replace(",", " "))
k3.metric("🟡 Arany összesen", f"{int(df_main['Gold'].sum()):,}".replace(",", " "))
k4.metric("⚪ Ezüst összesen", f"{int(df_main['Silver'].sum()):,}".replace(",", " "))
k5.metric("🟠 Bronz összesen", f"{int(df_main['Bronze'].sum()):,}".replace(",", " "))

st.divider()

# ─── Éremtípus-választó widget (mindkét diagramot vezérli) ───────────────────
medal_label = st.radio(
    "Válaszd ki az éremtípust!",
    options=list(MEDAL_OPTIONS.keys()),
    horizontal=True,
)
medal_col = MEDAL_OPTIONS[medal_label]
medal_color = MEDAL_COLORS[medal_col]

st.markdown("<br>", unsafe_allow_html=True)

# ─── Két fő diagram egymás mellett ──────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

# ── 1. Vonaldiagram: éremszám olimpiánként × földrészenként ─────────────────
with left:
    st.markdown(
        f"#### 📈 Éremszám olimpiánként – földrészenként &nbsp; `{medal_label}`"
    )

    line_df = (
        df_main.groupby(["Olimpics", "Continent"], observed=True)[
            ["Gold", "Silver", "Bronze", "Total"]
        ]
        .sum()
        .reset_index()
        .sort_values("Olimpics")
    )

    fig_line = go.Figure()

    for continent, color in CONTINENT_COLORS.items():
        sub = line_df[line_df["Continent"] == continent].sort_values("Olimpics")
        if sub.empty:
            continue
        trace_opacity = 1.0 if (selected is None or continent == selected) else 0.12
        fig_line.add_trace(
            go.Scatter(
                x=sub["Olimpics"].astype(str),
                y=sub[medal_col],
                name=continent,
                mode="lines+markers",
                opacity=trace_opacity,
                line=dict(color=color, width=3),
                marker=dict(
                    size=9, symbol="circle", line=dict(color="white", width=1.5)
                ),
                hovertemplate=f"<b>{continent}</b><br>%{{x}}<br>{medal_label}: <b>%{{y}}</b><extra></extra>",
            )
        )

    fig_line.update_layout(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#e0e0e0"),
        legend=dict(
            bgcolor="#161b22",
            bordercolor="#FFD700",
            borderwidth=1,
            font=dict(size=12),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            gridcolor="#21262d",
            tickfont=dict(size=11),
            title="",
            tickangle=-25,
        ),
        yaxis=dict(
            gridcolor="#21262d",
            title=dict(text=medal_label, font=dict(color=medal_color)),
            tickfont=dict(color=medal_color),
        ),
        height=430,
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )

    st.plotly_chart(fig_line, use_container_width=True)

# ── 2. Buborék-térkép: földrészek éremszáma ──────────────────────────────────
map_event = None

map_df = (
    df_main.groupby("Continent")[["Gold", "Silver", "Bronze", "Total"]]
    .sum()
    .reset_index()
)
map_df["lat"] = map_df["Continent"].map(lambda c: CONTINENT_CENTROIDS[c]["lat"])
map_df["lon"] = map_df["Continent"].map(lambda c: CONTINENT_CENTROIDS[c]["lon"])
map_df["color"] = map_df["Continent"].map(CONTINENT_COLORS)

with right:
    st.markdown(f"#### 🌍 Világ térkép – földrészenként &nbsp; `{medal_label}`")

    max_val = map_df[medal_col].max()

    bubble_opacities = [
        0.90 if (selected is None or c == selected) else 0.18
        for c in map_df["Continent"]
    ]

    fig_map = go.Figure()

    fig_map.add_trace(
        go.Scattergeo(
            lat=map_df["lat"],
            lon=map_df["lon"],
            text=map_df["Continent"],
            customdata=map_df[["Total", "Gold", "Silver", "Bronze"]].assign(
                _selected=map_df[medal_col]
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                f"{medal_label}: <b>%{{customdata[4]}}</b><br>"
                "─────────────<br>"
                "🟡 Arany: %{customdata[1]}<br>"
                "⚪ Ezüst: %{customdata[2]}<br>"
                "🟠 Bronz: %{customdata[3]}<br>"
                "🏅 Összes: %{customdata[0]}"
                "<extra></extra>"
            ),
            mode="markers+text",
            textposition="top center",
            textfont=dict(color="white", size=11, family="Arial Black"),
            marker=dict(
                size=map_df[medal_col] / max_val * 65 + 18,
                color=map_df["color"],
                opacity=bubble_opacities,
                line=dict(color="white", width=2),
            ),
        )
    )

    fig_map.update_layout(
        geo=dict(
            showland=True,
            landcolor="#1c2128",
            showocean=True,
            oceancolor="#0d1117",
            showcoastlines=True,
            coastlinecolor="#30363d",
            showcountries=True,
            countrycolor="#30363d",
            bgcolor="#0d1117",
            projection_type="natural earth",
            showframe=False,
        ),
        paper_bgcolor="#0d1117",
        font=dict(color="white"),
        height=430,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
    )

    if selected:
        st.caption(
            f"🔍 Kijelölve: **{selected}** — kattints rá újra a visszaállításhoz"
        )
    else:
        st.caption("👆 Kattints egy buborékra a szűréshez!")

    map_event = st.plotly_chart(
        fig_map,
        on_select="rerun",
        key=f"map_chart_{st.session_state.map_key}",
        use_container_width=True,
    )

# ─── Térkép kattintás feldolgozása ───────────────────────────────────────────
if map_event and map_event.selection and map_event.selection.points:
    point_idx = map_event.selection.points[0]["point_index"]
    clicked_continent = map_df.iloc[point_idx]["Continent"]
    if clicked_continent == selected:
        st.session_state.selected_continent = None
        st.session_state.map_key += 1
    else:
        st.session_state.selected_continent = clicked_continent
    st.rerun()

# ─── Összesített / top-10 sávdiagram ────────────────────────────────────────
st.divider()

if selected:
    st.markdown(f"#### 🏆 Top 10 ország — **{selected}** (arany / ezüst / bronz)")
    bar_source = (
        df_main[df_main["Continent"] == selected]
        .groupby("Country")[["Gold", "Silver", "Bronze", "Total"]]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=True)
        .tail(10)
    )
    bar_y = bar_source["Country"]
    bar_height = max(220, len(bar_source) * 42)
else:
    st.markdown(
        "#### 🏆 Összesített éremtáblázat – földrészenként (arany / ezüst / bronz)"
    )
    bar_source = (
        df_main.groupby("Continent")[["Gold", "Silver", "Bronze", "Total"]]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=True)
    )
    bar_y = bar_source["Continent"]
    bar_height = 310

fig_bar = go.Figure()
for col_name, col_label, col_color in [
    ("Bronze", "🟠 Bronz", "#CD7F32"),
    ("Silver", "⚪ Ezüst", "#C0C0C0"),
    ("Gold",   "🟡 Arany", "#FFD700"),
]:
    fig_bar.add_trace(
        go.Bar(
            y=bar_y,
            x=bar_source[col_name],
            name=col_label,
            orientation="h",
            marker_color=col_color,
            hovertemplate=f"<b>%{{y}}</b><br>{col_label}: <b>%{{x}}</b><extra></extra>",
        )
    )

fig_bar.update_layout(
    barmode="stack",
    plot_bgcolor="#0d1117",
    paper_bgcolor="#0d1117",
    font=dict(color="#e0e0e0"),
    legend=dict(
        bgcolor="#161b22",
        bordercolor="#FFD700",
        borderwidth=1,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    xaxis=dict(gridcolor="#21262d", title="Éremszám"),
    yaxis=dict(gridcolor="#21262d", title=""),
    height=bar_height,
    margin=dict(l=10, r=10, t=40, b=10),
)

st.plotly_chart(fig_bar, use_container_width=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <hr style="border-color:#21262d;">
    <p style="text-align:center; color:#555; font-size:0.82rem;">
        Kovács Gyula Picasso tréning &nbsp;·&nbsp;
        <a href="https://kovacsgyulacoach.hu/" target="_blank" style="color:#FFD700;">kovacsgyulacoach.hu</a>
        &nbsp;·&nbsp; Olimpiai adatok 1996–2024 &nbsp;·&nbsp;
        <em>Built with Streamlit + Plotly</em>
    </p>
    """,
    unsafe_allow_html=True,
)
