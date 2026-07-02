import os
from datetime import date
from html import escape
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURACION
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
LINUX_WAREHOUSE_DIR = Path("/mnt/d/mineria data/airflow/data/warehouse")
LINUX_BI_DB_PATH = LINUX_WAREHOUSE_DIR / "predictit_bi.duckdb"
LINUX_SOURCE_DB_PATH = LINUX_WAREHOUSE_DIR / "predictit.duckdb"
BI_DB_PATH = WAREHOUSE_DIR / "predictit_bi.duckdb"
SOURCE_DB_PATH = WAREHOUSE_DIR / "predictit.duckdb"
DEFAULT_DB_CANDIDATES = [
    LINUX_BI_DB_PATH,
    LINUX_SOURCE_DB_PATH,
    BI_DB_PATH,
    SOURCE_DB_PATH,
]
DEFAULT_DB_PATH = next((path for path in DEFAULT_DB_CANDIDATES if path.exists()), LINUX_SOURCE_DB_PATH)
SCHEMA = "main_marts"

REQUIRED_TABLES = {
    "mart_market_snapshot",
    "mart_top_movers",
    "mart_price_trends",
    "mart_rolling_averages",
    "mart_candidate_momentum",
    "mart_turning_points",
    "mart_volatility_analysis",
    "mart_spread_analysis",
    "mart_anomaly_detection",
}

st.set_page_config(
    page_title="PredictIt Analytics Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ESTILO VISUAL
# ============================================================
st.markdown(
    """
    <style>
        :root {
            --ink: #111827;
            --muted: #5b6472;
            --line: #d9dde4;
            --blue: #1266d6;
            --green: #137333;
            --red: #d01818;
            --yellow: #f5b700;
            --panel: #ffffff;
            --page: #f6f7f9;
            --nav: #101820;
        }

        .stApp {
            background: var(--page);
            color: var(--ink);
        }

        .block-container {
            padding: 1.05rem 1.45rem 1.35rem 1.45rem;
            max-width: 100%;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #101820 0%, #111820 58%, #0c1117 100%);
            border-right: 1px solid #05080c;
            min-width: 236px !important;
            width: 236px !important;
        }

        section[data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        section[data-testid="stSidebar"] .stRadio > label,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stCaption {
            color: #cbd5e1 !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            border-radius: 8px;
            padding: 0.45rem 0.55rem;
            margin-bottom: 0.25rem;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: #2b323a;
            border-left: 4px solid var(--yellow);
        }

        [data-testid="stHeader"] {
            background: rgba(246,247,249,0.88);
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.8rem;
        }

        .main-title {
            color: #101113;
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.05;
            margin: 0 0 0.2rem 0;
        }

        .main-subtitle {
            color: #333b45;
            font-size: 1.02rem;
            margin: 0;
        }

        .top-meta {
            color: #111827;
            font-size: 0.86rem;
            text-align: right;
            padding-top: 0.2rem;
        }

        .nav-logo {
            display: flex;
            align-items: end;
            gap: 4px;
            height: 68px;
            padding: 4px 8px 14px 8px;
            border-bottom: 1px solid rgba(255,255,255,.10);
            margin-bottom: 0.75rem;
        }

        .nav-logo span {
            display: inline-block;
            width: 10px;
            background: var(--yellow);
        }

        .nav-logo span:nth-child(1) { height: 17px; }
        .nav-logo span:nth-child(2) { height: 28px; }
        .nav-logo span:nth-child(3) { height: 39px; }
        .nav-logo span:nth-child(4) { height: 52px; }

        .filter-title {
            color: var(--yellow);
            font-weight: 800;
            margin: 0.8rem 0 0.35rem 0;
        }

        .kpi-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            min-height: 126px;
            padding: 1rem 1.05rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            box-shadow: 0 1px 2px rgba(15,23,42,.06);
        }

        .kpi-icon {
            font-size: 2.5rem;
            line-height: 1;
            font-weight: 900;
            min-width: 54px;
            text-align: center;
        }

        .kpi-label {
            font-size: 0.9rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .kpi-value {
            color: #050505;
            font-size: 2.05rem;
            font-weight: 900;
            line-height: 1.1;
        }

        .kpi-note {
            color: #20242a;
            font-size: 0.86rem;
            margin-top: 0.25rem;
        }

        .card-title {
            background: var(--panel);
            border: 1px solid var(--line);
            border-bottom: 0;
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 0.9rem 0.15rem 0.9rem;
            font-weight: 800;
            color: #111827;
            min-height: 44px;
        }

        .card-title span {
            color: #343a44;
            font-weight: 500;
        }

        .stDataFrame,
        div[data-testid="stPlotlyChart"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 0 0 8px 8px;
            padding: 0.3rem;
            box-shadow: 0 1px 2px rgba(15,23,42,.05);
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            padding: 14px;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(15,23,42,.06);
        }

        div[data-testid="stMetricLabel"] {
            color: #4b5563;
        }

        div[data-testid="stMetricValue"] {
            color: #111827;
        }

        .section-title {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 800;
            margin: 0.4rem 0 0.1rem 0;
        }

        .risk-box {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
        }

        .risk-high { color: var(--red); font-weight: 800; }
        .risk-mid { color: #a16207; font-weight: 800; }
        .risk-low { color: var(--green); font-weight: 800; }

        @media (max-width: 900px) {
            .main-title { font-size: 1.45rem; }
            .kpi-card { min-height: 110px; }
            .kpi-value { font-size: 1.55rem; }
            .kpi-icon { font-size: 2rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNCIONES BASE
# ============================================================
def resolve_db_path() -> str:
    env_path = os.getenv("PREDICTIT_DUCKDB_PATH")
    return env_path if env_path else str(DEFAULT_DB_PATH)


def db_exists(path: str) -> bool:
    try:
        return Path(path).expanduser().exists()
    except OSError:
        return False


@st.cache_data(ttl=300, show_spinner=False)
def run_query(path: str, sql: str, params=None) -> pd.DataFrame:
    with duckdb.connect(path, read_only=True) as con:
        return con.execute(sql, params or []).fetchdf()


def query(sql: str, params=None) -> pd.DataFrame:
    return run_query(db_path, sql, params)


def validate_connection() -> None:
    if not db_exists(db_path):
        st.error(
            "No encontre el archivo DuckDB. Cambia la ruta en la barra lateral. "
            "Recomendado: apunta a una copia como predictit_bi.duckdb."
        )
        st.stop()

    try:
        tables = query(
            f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{SCHEMA}'
            """
        )
    except Exception as exc:
        st.error("No pude abrir la base DuckDB.")
        st.exception(exc)
        st.stop()

    available = set(tables["table_name"].tolist())
    missing = sorted(REQUIRED_TABLES - available)
    if missing:
        st.error(
            "La base abre correctamente, pero faltan tablas esperadas en "
            f"`{SCHEMA}`: {', '.join(missing)}"
        )
        st.stop()


def latest_ts(table: str):
    df = query(f"SELECT MAX(extraction_ts) AS latest_ts FROM {SCHEMA}.{table}")
    if df.empty:
        return None
    return df.loc[0, "latest_ts"]


def safe_df(table: str, where_latest: bool = False) -> pd.DataFrame:
    if where_latest:
        ts = latest_ts(table)
        if pd.isna(ts):
            return pd.DataFrame()
        return query(f"SELECT * FROM {SCHEMA}.{table} WHERE extraction_ts = ?", [ts])
    return query(f"SELECT * FROM {SCHEMA}.{table}")


def short_text(value, max_len=58):
    if pd.isna(value):
        return ""
    value = str(value)
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def format_pct(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:.1%}"


def format_price(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:.3f}"


def compact_date(value):
    if pd.isna(value):
        return "N/A"
    try:
        return pd.to_datetime(value).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(value)


def card_title(title, subtitle=None):
    sub = f" <span>{escape(subtitle)}</span>" if subtitle else ""
    st.markdown(f'<div class="card-title">{escape(title)}{sub}</div>', unsafe_allow_html=True)


def kpi_card(icon, label, value, note, color):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="color:{color};">{icon}</div>
            <div>
                <div class="kpi-label" style="color:{color};">{escape(label)}</div>
                <div class="kpi-value">{escape(str(value))}</div>
                <div class="kpi-note">{escape(str(note))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_plot(fig, height=360):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=12, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827", size=12),
        xaxis=dict(gridcolor="#e5e7eb", zeroline=False),
        yaxis=dict(gridcolor="#e5e7eb", zeroline=False),
        legend=dict(font=dict(size=11)),
    )
    return fig


def make_bar(df, x, y, title=None, hover_data=None, orientation="h", height=360, color="#1266d6"):
    if df.empty:
        st.info("No hay datos disponibles para este visual.")
        return

    fig = px.bar(
        df,
        x=x,
        y=y,
        orientation=orientation,
        title=title,
        hover_data=hover_data or [],
        color_discrete_sequence=[color],
        text=x if orientation == "h" else y,
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    st.plotly_chart(style_plot(fig, height), use_container_width=True)


def make_line(df, x, y, title, color=None, height=430):
    if df.empty:
        st.info("No hay datos disponibles para este visual.")
        return

    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title)
    st.plotly_chart(style_plot(fig, height), use_container_width=True)


def metric_row(metrics):
    cols = st.columns(len(metrics))
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label, value, delta)


def rolling_average_chart(df, title):
    if df.empty:
        st.info("No hay rolling averages para este contrato.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["snapshot_date"], y=df["close_price"], mode="lines+markers", name="Close"))
    fig.add_trace(go.Scatter(x=df["snapshot_date"], y=df["avg_7d"], mode="lines+markers", name="Avg 7d"))
    fig.add_trace(go.Scatter(x=df["snapshot_date"], y=df["avg_14d"], mode="lines+markers", name="Avg 14d"))
    fig.add_trace(go.Scatter(x=df["snapshot_date"], y=df["avg_30d"], mode="lines+markers", name="Avg 30d"))
    fig.update_layout(title=title)
    st.plotly_chart(style_plot(fig), use_container_width=True)


def contract_price_history(trends, selected):
    if trends.empty:
        return pd.DataFrame()

    return (
        trends[trends["contract_name"] == selected]
        .groupby("snapshot_date", as_index=False)
        .agg(
            avg_price=("avg_last_trade_price", "mean"),
            max_price=("max_last_trade_price", "max"),
            min_price=("min_last_trade_price", "min"),
            observations=("observations", "sum"),
        )
        .sort_values("snapshot_date")
    )


def filter_by_selection(df, market, contract):
    filtered = df.copy()
    if market != "Todos" and "market_name" in filtered.columns:
        filtered = filtered[filtered["market_name"] == market]
    if contract != "Todos" and "contract_name" in filtered.columns:
        filtered = filtered[filtered["contract_name"] == contract]
    return filtered


with st.sidebar:
    st.markdown(
        """
        <div class="nav-logo">
            <span></span><span></span><span></span><span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navegacion",
        [
            "Overview",
            "Trends",
            "Risk & Anomalies",
            "Contract Detail",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown('<div class="filter-title">Filtros Globales</div>', unsafe_allow_html=True)
    db_path = st.text_input(
        "DuckDB",
        value=resolve_db_path(),
        help="Usa preferiblemente una copia de lectura: predictit_bi.duckdb",
    )
    st.caption(f"Fuente: {SCHEMA}.*")


validate_connection()


# ============================================================
# PAGINA 1: EXECUTIVE OVERVIEW
# ============================================================
def executive_overview():
    snapshot = safe_df("mart_market_snapshot", where_latest=True)
    movers = safe_df("mart_top_movers", where_latest=True)
    anomalies = safe_df("mart_anomaly_detection", where_latest=True)
    volatility = safe_df("mart_volatility_analysis", where_latest=True)
    spreads = safe_df("mart_spread_analysis", where_latest=True)

    if snapshot.empty:
        st.warning("No hay datos en mart_market_snapshot.")
        return

    latest = snapshot["extraction_ts"].max() if "extraction_ts" in snapshot.columns else None
    market_options = ["Todos"] + sorted(snapshot["market_name"].dropna().unique().tolist())
    contract_options = ["Todos"] + sorted(snapshot["contract_name"].dropna().unique().tolist())

    header_left, date_col, market_col, contract_col, refresh_col = st.columns([2.7, 0.95, 1.05, 1.15, 1.05])
    with header_left:
        st.markdown('<div class="main-title">PredictIt Analytics Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<p class="main-subtitle">Executive Overview</p>', unsafe_allow_html=True)
    with date_col:
        selected_date = pd.to_datetime(latest).date() if not pd.isna(latest) else date.today()
        st.date_input("Fecha", value=selected_date)
    with market_col:
        selected_market = st.selectbox("Market", market_options, index=0)
    with contract_col:
        selected_contract = st.selectbox("Contrato", contract_options, index=0)
    with refresh_col:
        st.markdown(
            f"""
            <div class="top-meta">
                <div>Ultima actualizacion</div>
                <strong>{compact_date(latest)}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Refrescar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    snapshot_view = filter_by_selection(snapshot, selected_market, selected_contract)
    movers_view = filter_by_selection(movers, selected_market, selected_contract)
    anomalies_view = filter_by_selection(anomalies, selected_market, selected_contract)
    spreads_view_all = filter_by_selection(spreads, selected_market, selected_contract)

    markets = snapshot_view["market_id"].nunique()
    contracts = snapshot_view["contract_id"].nunique()
    avg_price = snapshot_view["last_trade_price"].mean()
    active_anomalies = anomalies_view[anomalies_view["is_anomaly"] == True].shape[0] if not anomalies_view.empty else 0
    max_gain_row = movers_view.sort_values("change_pct", ascending=False).head(1)
    max_loss_row = movers_view.sort_values("change_pct", ascending=True).head(1)
    max_gain = max_gain_row["change_pct"].iloc[0] if not max_gain_row.empty else None
    max_loss = max_loss_row["change_pct"].iloc[0] if not max_loss_row.empty else None
    max_gain_name = short_text(max_gain_row["contract_name"].iloc[0], 20) if not max_gain_row.empty else "N/A"
    max_loss_name = short_text(max_loss_row["contract_name"].iloc[0], 20) if not max_loss_row.empty else "N/A"

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        kpi_card("◎", "Total Markets", f"{markets:,}", "Mercados activos", "#1266d6")
    with k2:
        kpi_card("▤", "Total Contracts", f"{contracts:,}", "Contratos activos", "#166534")
    with k3:
        kpi_card("↗", "Precio Promedio Actual", format_price(avg_price), "Promedio de precio", "#6d28d9")
    with k4:
        kpi_card("▲", "Mayor Gainer (24h)", format_pct(max_gain), max_gain_name, "#168a2f")
    with k5:
        kpi_card("▼", "Mayor Loser (24h)", format_pct(max_loss), max_loss_name, "#dc1f1f")
    with k6:
        kpi_card("!", "Anomalias Activas", f"{active_anomalies:,}", "Senales activas", "#f97316")

    c1, c2, c3 = st.columns([1.15, 1.08, 1.12])

    with c1:
        card_title("Top Movers", "(24h)")
        if not movers_view.empty:
            movers_table = movers_view.sort_values("change_pct", ascending=False).head(6).copy()
            movers_table["Contrato"] = movers_table["contract_name"].apply(lambda x: short_text(x, 25))
            movers_table["Mercado"] = movers_table["market_name"].apply(lambda x: short_text(x, 34))
            movers_table["Precio Actual"] = movers_table["price_now"].map(format_price)
            movers_table["Cambio % (24h)"] = movers_table["change_pct"].map(format_pct)
            st.dataframe(
                movers_table[["Contrato", "Mercado", "Precio Actual", "Cambio % (24h)"]],
                hide_index=True,
                use_container_width=True,
                height=330,
            )
        else:
            st.info("No hay datos de movers.")

    with c2:
        card_title("Lideres por Mercado", "(Top mercados por # contratos)")
        leaders = (
            snapshot_view.groupby(["market_name", "contract_name"], as_index=False)
            .agg(price=("last_trade_price", "mean"), contracts=("contract_count", "max"))
            .sort_values(["contracts", "price"], ascending=False)
            .head(6)
        )
        if not leaders.empty:
            leaders["market_short"] = leaders["market_name"].apply(lambda x: short_text(x, 26))
            leaders["contract_short"] = leaders["contract_name"].apply(lambda x: short_text(x, 24))
            fig = px.bar(
                leaders.sort_values("price"),
                x="price",
                y="market_short",
                orientation="h",
                text="contract_short",
                hover_data=["contract_name", "market_name", "contracts"],
                color_discrete_sequence=["#1266d6"],
            )
            fig.update_traces(textposition="inside", insidetextanchor="start", textfont_color="#ffffff")
            fig.update_xaxes(title="Precio", range=[0, max(1.0, leaders["price"].max() * 1.08)])
            fig.update_yaxes(title="")
            st.plotly_chart(style_plot(fig, 330), use_container_width=True)
        else:
            st.info("No hay lideres para mostrar.")

    with c3:
        card_title("Distribucion de Contratos por Mercado")
        market_dist = (
            snapshot_view.groupby("market_name", as_index=False)
            .agg(contracts=("contract_id", "nunique"))
            .sort_values("contracts", ascending=False)
        )
        if not market_dist.empty:
            top_dist = market_dist.head(5).copy()
            others = market_dist.iloc[5:]["contracts"].sum()
            if others:
                top_dist = pd.concat(
                    [
                        pd.DataFrame([{"market_name": "Otros mercados", "contracts": others}]),
                        top_dist,
                    ],
                    ignore_index=True,
                )
            fig = px.pie(
                top_dist,
                names="market_name",
                values="contracts",
                hole=0.52,
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig.update_traces(textinfo="none")
            fig.add_annotation(
                text=f"<b>{contracts:,}</b><br>Total",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=22, color="#111827"),
            )
            st.plotly_chart(style_plot(fig, 330), use_container_width=True)
        else:
            st.info("No hay distribucion disponible.")

    b1, b2, b3 = st.columns([1.15, 1.08, 1.12])

    with b1:
        card_title("Snapshot del Mercado", "(Tiempo Real)")
        market_snapshot = (
            snapshot_view.groupby("market_name", as_index=False)
            .agg(
                Contratos=("contract_id", "nunique"),
                Precio_Prom=("last_trade_price", "mean"),
                Spread_Prom=("spread_yes", "mean"),
            )
            .sort_values("Contratos", ascending=False)
            .head(6)
        )
        if not market_snapshot.empty:
            market_snapshot["Mercado"] = market_snapshot["market_name"].apply(lambda x: short_text(x, 42))
            market_snapshot["Precio Prom."] = market_snapshot["Precio_Prom"].map(format_price)
            market_snapshot["Spread Prom."] = market_snapshot["Spread_Prom"].map(format_price)
            st.dataframe(
                market_snapshot[["Mercado", "Contratos", "Precio Prom.", "Spread Prom."]],
                hide_index=True,
                use_container_width=True,
                height=300,
            )
        else:
            st.info("No hay snapshot para mostrar.")

    with b2:
        card_title("Anomalias Activas", "(Senales de Alerta)")
        if not anomalies_view.empty:
            anom_table = anomalies_view[anomalies_view["is_anomaly"] == True].copy()
            anom_table["Contrato"] = anom_table["contract_name"].apply(lambda x: short_text(x, 24))
            anom_table["Mercado"] = anom_table["market_name"].apply(lambda x: short_text(x, 32))
            anom_table["Z-Score"] = anom_table["z_score"].map(lambda x: f"{x:+.2f}" if not pd.isna(x) else "N/A")
            anom_table["Fuerza"] = anom_table["signal_strength"].fillna("N/A")
            st.dataframe(
                anom_table[["Contrato", "Mercado", "Z-Score", "Fuerza"]]
                .sort_values("Z-Score", ascending=False)
                .head(6),
                hide_index=True,
                use_container_width=True,
                height=300,
            )
        else:
            st.info("No hay anomalias activas en el ultimo snapshot.")

    with b3:
        card_title("Spreads Mas Amplios")
        if not spreads_view_all.empty:
            spreads_view = spreads_view_all.dropna(subset=["current_spread_yes"]).copy()
            spreads_view["contract_short"] = spreads_view["contract_name"].apply(lambda x: short_text(x, 16))
            top_spreads = spreads_view.sort_values("current_spread_yes", ascending=False).head(5)
            fig = px.bar(
                top_spreads,
                x="contract_short",
                y="current_spread_yes",
                text="current_spread_yes",
                color_discrete_sequence=["#1266d6"],
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_xaxes(title="")
            fig.update_yaxes(title="Spread Prom.", range=[0, max(1.0, top_spreads["current_spread_yes"].max() * 1.2)])
            st.plotly_chart(style_plot(fig, 300), use_container_width=True)
        else:
            st.info("No hay datos de spreads.")


# ============================================================
# PAGINA 2: HISTORICAL TRENDS
# ============================================================
def historical_trends():
    st.markdown('<div class="main-title">Historical Trends</div>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Tendencias historicas, promedios moviles, momentum y puntos de giro.</p>', unsafe_allow_html=True)

    momentum = safe_df("mart_candidate_momentum")
    rolling = safe_df("mart_rolling_averages")
    trends = safe_df("mart_price_trends")
    turning = safe_df("mart_turning_points")

    selected_contract = None
    if not momentum.empty:
        options = momentum.sort_values("momentum_rank")["contract_name"].dropna().unique().tolist()
        selected_contract = st.sidebar.selectbox("Contrato para tendencia", options, index=0)

    if selected_contract:
        current = momentum[momentum["contract_name"] == selected_contract].head(1)
        if not current.empty:
            row = current.iloc[0]
            metric_row(
                [
                    ("Contrato", short_text(row["contract_name"], 28), None),
                    ("Precio actual", format_price(row.get("current_price")), None),
                    ("Cambio diario promedio", format_price(row.get("avg_daily_change")), None),
                    ("Cambio 30d", format_price(row.get("total_change_30d")), None),
                    ("Momentum", str(row.get("momentum_direction", "N/A")), None),
                ]
            )

    c1, c2 = st.columns([1.15, 1])

    with c1:
        card_title("Evolucion de precio")
        if selected_contract:
            t = contract_price_history(trends, selected_contract)
            make_line(t, "snapshot_date", "avg_price", f"Evolucion de precio: {short_text(selected_contract, 50)}")

    with c2:
        card_title("Promedios moviles")
        if selected_contract and not rolling.empty:
            r = rolling[rolling["contract_name"] == selected_contract].sort_values("snapshot_date")
            rolling_average_chart(r, "Close vs promedios moviles")

    c3, c4 = st.columns(2)

    with c3:
        card_title("Top Momentum")
        if not momentum.empty:
            cols = [
                "momentum_rank",
                "contract_name",
                "market_name",
                "avg_daily_change",
                "total_change_30d",
                "momentum_direction",
                "current_price",
            ]
            st.dataframe(
                momentum[[c for c in cols if c in momentum.columns]].sort_values("momentum_rank").head(30),
                use_container_width=True,
                hide_index=True,
            )

    with c4:
        card_title("Turning Points significativos")
        if not turning.empty:
            view = turning[turning["is_significant"] == True].copy()
            cols = [
                "snapshot_date",
                "contract_name",
                "market_name",
                "price_before",
                "price_after",
                "impact",
                "impact_pct",
                "trend_direction",
            ]
            st.dataframe(
                view[[c for c in cols if c in view.columns]]
                .sort_values("impact_pct", key=lambda s: s.abs(), ascending=False)
                .head(40),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# PAGINA 3: RISK & ANOMALIES
# ============================================================
def risk_anomalies():
    st.markdown('<div class="main-title">Risk & Anomalies</div>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Analisis de anomalias, z-score, volatilidad, spreads y liquidez.</p>', unsafe_allow_html=True)

    anomalies = safe_df("mart_anomaly_detection", where_latest=True)
    volatility = safe_df("mart_volatility_analysis", where_latest=True)
    spreads = safe_df("mart_spread_analysis", where_latest=True)

    active = anomalies[anomalies["is_anomaly"] == True] if not anomalies.empty else pd.DataFrame()
    z_extreme = anomalies["z_score"].abs().max() if not anomalies.empty else None
    avg_vol = volatility["volatility_score"].mean() if not volatility.empty else None
    avg_spread = spreads["avg_spread_yes"].mean() if not spreads.empty else None
    max_spread = spreads["current_spread_yes"].max() if not spreads.empty else None

    metric_row(
        [
            ("Active Anomalies", f"{len(active):,}", None),
            ("Contracts Evaluated", f"{len(anomalies):,}", None),
            ("Extreme Z-Score", format_price(z_extreme), None),
            ("Avg Volatility", format_price(avg_vol), None),
            ("Avg Spread YES", format_price(avg_spread), None),
            ("Max Current Spread", format_price(max_spread), None),
        ]
    )

    c1, c2 = st.columns(2)

    with c1:
        card_title("Anomalias por z-score absoluto")
        if not active.empty:
            active_view = active.copy()
            active_view["contract_short"] = active_view["contract_name"].apply(lambda x: short_text(x, 40))
            active_view["abs_z"] = active_view["z_score"].abs()
            make_bar(
                active_view.sort_values("abs_z", ascending=False).head(12).sort_values("abs_z"),
                x="abs_z",
                y="contract_short",
                hover_data=["market_name", "z_score", "current_price", "signal_strength"],
            )
        else:
            st.info("No hay anomalias activas en el ultimo snapshot.")

    with c2:
        card_title("Volatilidad vs precio actual")
        if not volatility.empty:
            vol30 = volatility[volatility["window_days"] == 30].copy()
            fig = px.scatter(
                vol30.dropna(subset=["volatility_score"]),
                x="current_price",
                y="volatility_score",
                size="price_range",
                hover_name="contract_name",
                hover_data=["market_name", "avg_price", "stddev_price"],
                color_discrete_sequence=["#1266d6"],
            )
            st.plotly_chart(style_plot(fig, 420), use_container_width=True)

    c3, c4 = st.columns([1.1, 1])

    with c3:
        card_title("Tabla de anomalias")
        if not anomalies.empty:
            view = anomalies.copy()
            cols = [
                "contract_name",
                "market_name",
                "current_price",
                "avg_price_30d",
                "stddev_price_30d",
                "z_score",
                "is_anomaly",
                "change_24h",
                "anomaly_score",
                "signal_strength",
            ]
            st.dataframe(
                view[[c for c in cols if c in view.columns]]
                .sort_values("z_score", key=lambda s: s.abs(), ascending=False)
                .head(60),
                use_container_width=True,
                hide_index=True,
            )

    with c4:
        card_title("Spreads y liquidez")
        if not spreads.empty:
            view = spreads.dropna(subset=["current_spread_yes"]).copy()
            view["contract_short"] = view["contract_name"].apply(lambda x: short_text(x, 38))
            make_bar(
                view.sort_values("current_spread_yes", ascending=False).head(12).sort_values("current_spread_yes"),
                x="current_spread_yes",
                y="contract_short",
                hover_data=["market_name", "avg_spread_yes", "max_spread_yes"],
            )

    risk_level = "LOW"
    if active.shape[0] > 100 or (z_extreme is not None and z_extreme > 10):
        risk_level = "HIGH"
    elif active.shape[0] > 25 or (z_extreme is not None and z_extreme > 4):
        risk_level = "MEDIUM"

    cls = "risk-high" if risk_level == "HIGH" else "risk-mid" if risk_level == "MEDIUM" else "risk-low"
    st.markdown(
        f"""
        <div class="risk-box">
            <div>Nivel estimado: <span class="{cls}">{risk_level}</span></div>
            <div>
                Basado en anomalias activas, z-score extremo, volatilidad promedio y spreads actuales.
                Este resumen es una regla operativa, no una recomendacion financiera.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGINA 4: CONTRACT DETAIL
# ============================================================
def contract_detail():
    st.markdown('<div class="main-title">Contract Detail</div>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Vista de auditoria para revisar un contrato especifico.</p>', unsafe_allow_html=True)

    snapshot = safe_df("mart_market_snapshot", where_latest=True)
    movers = safe_df("mart_top_movers", where_latest=True)
    anomalies = safe_df("mart_anomaly_detection", where_latest=True)
    volatility = safe_df("mart_volatility_analysis", where_latest=True)
    spreads = safe_df("mart_spread_analysis", where_latest=True)
    rolling = safe_df("mart_rolling_averages")
    trends = safe_df("mart_price_trends")
    turning = safe_df("mart_turning_points")

    if snapshot.empty:
        st.warning("No hay datos para Contract Detail.")
        return

    contracts = snapshot.sort_values("last_trade_price", ascending=False)["contract_name"].dropna().unique().tolist()
    selected = st.sidebar.selectbox("Selecciona contrato", contracts, index=0)

    current = snapshot[snapshot["contract_name"] == selected].head(1)
    mover = movers[movers["contract_name"] == selected].head(1) if not movers.empty else pd.DataFrame()
    anom = anomalies[anomalies["contract_name"] == selected].head(1) if not anomalies.empty else pd.DataFrame()
    spread = spreads[spreads["contract_name"] == selected].head(1) if not spreads.empty else pd.DataFrame()
    vol = (
        volatility[(volatility["contract_name"] == selected) & (volatility["window_days"] == 30)].head(1)
        if not volatility.empty
        else pd.DataFrame()
    )

    price = current.iloc[0]["last_trade_price"] if not current.empty else None
    last_close = current.iloc[0]["last_close_price"] if not current.empty else None
    change_24h = mover.iloc[0]["change_pct"] if not mover.empty else None
    z_score = anom.iloc[0]["z_score"] if not anom.empty else None
    vol_score = vol.iloc[0]["volatility_score"] if not vol.empty else None
    curr_spread = spread.iloc[0]["current_spread_yes"] if not spread.empty else None

    metric_row(
        [
            ("Precio actual", format_price(price), None),
            ("Last Close", format_price(last_close), None),
            ("Cambio 24h", format_pct(change_24h), None),
            ("Z-Score", format_price(z_score), None),
            ("Volatility Score", format_price(vol_score), None),
            ("Spread YES", format_price(curr_spread), None),
        ]
    )

    if not current.empty:
        st.markdown(
            f"""
            <div class="risk-box">
                <b>Contrato:</b> {escape(selected)}<br>
                <b>Mercado:</b> {escape(str(current.iloc[0]["market_name"]))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)

    with c1:
        card_title("Precio historico promedio")
        t = contract_price_history(trends, selected)
        make_line(t, "snapshot_date", "avg_price", "Precio historico promedio")

    with c2:
        card_title("Close vs promedios moviles")
        r = rolling[rolling["contract_name"] == selected].sort_values("snapshot_date")
        rolling_average_chart(r, "Close vs promedios moviles")

    c3, c4 = st.columns(2)

    with c3:
        card_title("Turning Points")
        tp = turning[turning["contract_name"] == selected].copy()
        cols = [
            "snapshot_date",
            "price_before",
            "price_after",
            "impact",
            "impact_pct",
            "is_significant",
            "trend_direction",
        ]
        st.dataframe(
            tp[[c for c in cols if c in tp.columns]].sort_values("snapshot_date", ascending=False).head(30),
            use_container_width=True,
            hide_index=True,
        )

    with c4:
        card_title("Riesgo y microestructura")
        detail_rows = []

        if not anom.empty:
            a = anom.iloc[0]
            detail_rows.extend(
                [
                    {"Metrica": "Precio actual", "Valor": format_price(a.get("current_price"))},
                    {"Metrica": "Avg 30d", "Valor": format_price(a.get("avg_price_30d"))},
                    {"Metrica": "StdDev 30d", "Valor": format_price(a.get("stddev_price_30d"))},
                    {"Metrica": "Z-Score", "Valor": format_price(a.get("z_score"))},
                    {"Metrica": "Anomalia", "Valor": str(a.get("is_anomaly"))},
                    {"Metrica": "Signal Strength", "Valor": str(a.get("signal_strength"))},
                ]
            )

        if not spread.empty:
            s = spread.iloc[0]
            detail_rows.extend(
                [
                    {"Metrica": "Avg Spread YES", "Valor": format_price(s.get("avg_spread_yes"))},
                    {"Metrica": "Max Spread YES", "Valor": format_price(s.get("max_spread_yes"))},
                    {"Metrica": "Current Spread YES", "Valor": format_price(s.get("current_spread_yes"))},
                    {"Metrica": "Implied Volatility", "Valor": format_price(s.get("implied_volatility"))},
                ]
            )

        if not vol.empty:
            v = vol.iloc[0]
            detail_rows.extend(
                [
                    {"Metrica": "Window Days", "Valor": str(v.get("window_days"))},
                    {"Metrica": "Volatility Score", "Valor": format_price(v.get("volatility_score"))},
                    {"Metrica": "Price Range", "Valor": format_price(v.get("price_range"))},
                ]
            )

        st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)


# ============================================================
# ROUTER
# ============================================================
if page == "Overview":
    executive_overview()
elif page == "Trends":
    historical_trends()
elif page == "Risk & Anomalies":
    risk_anomalies()
else:
    contract_detail()
