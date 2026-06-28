import os
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================
# Cambia esta ruta por la ubicación real de tu archivo DuckDB.
# Recomendado: usa una copia solo para BI, por ejemplo predictit_bi.duckdb.
DEFAULT_DB_PATH = r"/mnt/d/mineria data/airflow/data/warehouse/predictit.duckdb"
SCHEMA = "main_marts"

st.set_page_config(
    page_title="PredictIt Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ESTILO VISUAL
# ============================================================
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.2rem;
        }

        div[data-testid="stMetric"] {
            background-color: #111827;
            border: 1px solid #263244;
            padding: 16px;
            border-radius: 14px;
            box-shadow: 0 1px 2px rgba(0,0,0,.25);
        }

        div[data-testid="stMetricLabel"] {
            color: #9CA3AF;
        }

        div[data-testid="stMetricValue"] {
            color: #F9FAFB;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.25rem;
        }

        .small-note {
            color: #9CA3AF;
            font-size: 0.84rem;
            margin-bottom: 1rem;
        }

        .risk-box {
            background-color: #111827;
            border: 1px solid #263244;
            border-radius: 14px;
            padding: 16px;
            margin-top: 4px;
        }

        .risk-high {
            color: #F87171;
            font-weight: 700;
        }

        .risk-mid {
            color: #FBBF24;
            font-weight: 700;
        }

        .risk-low {
            color: #34D399;
            font-weight: 700;
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
    if env_path:
        return env_path
    return DEFAULT_DB_PATH


with st.sidebar:
    st.title("PredictIt BI")
    st.caption("Dashboard Streamlit + DuckDB")

    db_path = st.text_input(
        "Ruta del archivo .duckdb",
        value=resolve_db_path(),
        help="Usa preferiblemente una copia de lectura: predictit_bi.duckdb",
    )

    st.divider()
    page = st.radio(
        "Página",
        [
            "1. Executive Overview",
            "2. Historical Trends",
            "3. Risk & Anomalies",
            "4. Contract Detail",
        ],
    )

    st.divider()
    st.caption("Fuente esperada:")
    st.code("main_marts.*", language="text")


def db_exists(path: str) -> bool:
    try:
        return Path(path).exists()
    except Exception:
        return False


@st.cache_data(ttl=300, show_spinner=False)
def run_query(db_path: str, sql: str, params=None) -> pd.DataFrame:
    if params is None:
        params = []
    with duckdb.connect(db_path, read_only=True) as con:
        return con.execute(sql, params).fetchdf()


def query(sql: str, params=None) -> pd.DataFrame:
    return run_query(db_path, sql, params)


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
    return f"{x:.2%}"


def format_price(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:.3f}"


def make_bar(df, x, y, title, hover_data=None, orientation="h", height=420):
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
    )
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E5E7EB"),
        title_font=dict(size=16),
        xaxis=dict(gridcolor="#263244"),
        yaxis=dict(gridcolor="#263244"),
    )
    st.plotly_chart(fig, use_container_width=True)


def make_line(df, x, y, title, color=None, height=430):
    if df.empty:
        st.info("No hay datos disponibles para este visual.")
        return

    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title)
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E5E7EB"),
        title_font=dict(size=16),
        xaxis=dict(gridcolor="#263244"),
        yaxis=dict(gridcolor="#263244"),
    )
    st.plotly_chart(fig, use_container_width=True)


def metric_row(metrics):
    cols = st.columns(len(metrics))
    for col, item in zip(cols, metrics):
        label, value, delta = item
        col.metric(label, value, delta)


def validate_connection():
    if not db_exists(db_path):
        st.error(
            "No encontré el archivo DuckDB. Cambia la ruta en la barra lateral. "
            "Recomendado: apunta a una copia como predictit_bi.duckdb."
        )
        st.stop()

    try:
        _ = query(f"""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = '{SCHEMA}'
            LIMIT 1
        """)
    except Exception as e:
        st.error("No pude abrir la base DuckDB.")
        st.exception(e)
        st.stop()


validate_connection()


# ============================================================
# PÁGINA 1: EXECUTIVE OVERVIEW
# ============================================================
def executive_overview():
    st.title("Executive Overview")
    st.caption("Estado actual del mercado, líderes, movimientos de 24h y alertas activas.")

    snapshot = safe_df("mart_market_snapshot", where_latest=True)
    movers = safe_df("mart_top_movers", where_latest=True)
    anomalies = safe_df("mart_anomaly_detection", where_latest=True)
    volatility = safe_df("mart_volatility_analysis", where_latest=True)
    spreads = safe_df("mart_spread_analysis", where_latest=True)

    if snapshot.empty:
        st.warning("No hay datos en mart_market_snapshot.")
        return

    markets = snapshot["market_id"].nunique()
    contracts = snapshot["contract_id"].nunique()
    avg_price = snapshot["last_trade_price"].mean()
    avg_spread = snapshot["spread_yes"].mean(skipna=True)

    active_anomalies = 0
    if not anomalies.empty and "is_anomaly" in anomalies.columns:
        active_anomalies = anomalies[anomalies["is_anomaly"] == True].shape[0]

    max_gain = movers["change_pct"].max() if not movers.empty else None
    max_loss = movers["change_pct"].min() if not movers.empty else None

    metric_row(
        [
            ("Markets", f"{markets:,}", None),
            ("Contracts", f"{contracts:,}", None),
            ("Avg Price", format_price(avg_price), None),
            ("Avg Spread YES", format_price(avg_spread), None),
            ("Max 24h Gain", format_pct(max_gain), None),
            ("Active Anomalies", f"{active_anomalies:,}", None),
        ]
    )

    st.markdown('<div class="section-title">Movimientos y líderes</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])

    with c1:
        if not movers.empty:
            top_gainers = movers.sort_values("change_pct", ascending=False).head(10).copy()
            top_gainers["contract_short"] = top_gainers["contract_name"].apply(lambda x: short_text(x, 42))
            make_bar(
                top_gainers.sort_values("change_pct"),
                x="change_pct",
                y="contract_short",
                title="Top Gainers 24h",
                hover_data=["market_name", "price_now", "price_24h_ago", "direction"],
            )

    with c2:
        top_markets = (
            snapshot.groupby(["market_id", "market_name"], as_index=False)
            .agg(
                contracts=("contract_count", "max"),
                avg_price=("last_trade_price", "mean"),
                avg_spread_yes=("spread_yes", "mean"),
            )
            .sort_values("contracts", ascending=False)
            .head(10)
        )
        top_markets["market_short"] = top_markets["market_name"].apply(lambda x: short_text(x, 45))
        make_bar(
            top_markets.sort_values("contracts"),
            x="contracts",
            y="market_short",
            title="Mercados con más contratos",
            hover_data=["market_name", "avg_price", "avg_spread_yes"],
        )

    c3, c4 = st.columns([1.05, 1])

    with c3:
        st.markdown('<div class="section-title">Snapshot actual</div>', unsafe_allow_html=True)
        show_cols = [
            "market_name",
            "contract_name",
            "last_trade_price",
            "last_close_price",
            "price_change_from_last_close",
            "spread_yes",
            "spread_no",
            "contract_count",
        ]
        available = [c for c in show_cols if c in snapshot.columns]
        st.dataframe(
            snapshot[available]
            .sort_values("last_trade_price", ascending=False)
            .head(40),
            use_container_width=True,
            hide_index=True,
        )

    with c4:
        st.markdown('<div class="section-title">Anomalías activas</div>', unsafe_allow_html=True)
        if not anomalies.empty:
            anom_view = anomalies[anomalies["is_anomaly"] == True].copy()
            anom_cols = [
                "contract_name",
                "market_name",
                "current_price",
                "z_score",
                "change_24h",
                "anomaly_score",
                "signal_strength",
                "signal_type",
            ]
            available = [c for c in anom_cols if c in anom_view.columns]
            st.dataframe(
                anom_view[available]
                .sort_values("z_score", key=lambda s: s.abs(), ascending=False)
                .head(30),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No hay tabla de anomalías disponible.")

    st.markdown('<div class="section-title">Riesgo de mercado</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)

    with c5:
        if not volatility.empty:
            vol30 = volatility[volatility["window_days"] == 30].copy()
            vol30["contract_short"] = vol30["contract_name"].apply(lambda x: short_text(x, 42))
            make_bar(
                vol30.sort_values("volatility_score", ascending=False).head(10).sort_values("volatility_score"),
                x="volatility_score",
                y="contract_short",
                title="Contratos más volátiles - 30 días",
                hover_data=["market_name", "current_price", "price_range"],
            )

    with c6:
        if not spreads.empty:
            spreads_view = spreads.dropna(subset=["current_spread_yes"]).copy()
            spreads_view["contract_short"] = spreads_view["contract_name"].apply(lambda x: short_text(x, 42))
            make_bar(
                spreads_view.sort_values("current_spread_yes", ascending=False)
                .head(10)
                .sort_values("current_spread_yes"),
                x="current_spread_yes",
                y="contract_short",
                title="Spreads más amplios",
                hover_data=["market_name", "avg_spread_yes", "max_spread_yes"],
            )


# ============================================================
# PÁGINA 2: HISTORICAL TRENDS
# ============================================================
def historical_trends():
    st.title("Historical Trends")
    st.caption("Tendencias históricas, promedios móviles, momentum y puntos de giro.")

    momentum = query(f"SELECT * FROM {SCHEMA}.mart_candidate_momentum")
    rolling = query(f"SELECT * FROM {SCHEMA}.mart_rolling_averages")
    trends = query(f"SELECT * FROM {SCHEMA}.mart_price_trends")
    turning = query(f"SELECT * FROM {SCHEMA}.mart_turning_points")

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
        if selected_contract and not trends.empty:
            t = (
                trends[trends["contract_name"] == selected_contract]
                .groupby("snapshot_date", as_index=False)
                .agg(
                    avg_price=("avg_last_trade_price", "mean"),
                    max_price=("max_last_trade_price", "max"),
                    min_price=("min_last_trade_price", "min"),
                    observations=("observations", "sum"),
                )
                .sort_values("snapshot_date")
            )
            make_line(t, "snapshot_date", "avg_price", f"Evolución de precio: {short_text(selected_contract, 50)}")

    with c2:
        if selected_contract and not rolling.empty:
            r = rolling[rolling["contract_name"] == selected_contract].sort_values("snapshot_date")
            if not r.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["close_price"], mode="lines+markers", name="Close"))
                fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["avg_7d"], mode="lines+markers", name="Avg 7d"))
                fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["avg_14d"], mode="lines+markers", name="Avg 14d"))
                fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["avg_30d"], mode="lines+markers", name="Avg 30d"))
                fig.update_layout(
                    title="Close vs promedios móviles",
                    height=430,
                    margin=dict(l=10, r=10, t=50, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E5E7EB"),
                    xaxis=dict(gridcolor="#263244"),
                    yaxis=dict(gridcolor="#263244"),
                )
                st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-title">Top Momentum</div>', unsafe_allow_html=True)
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
                momentum[[c for c in cols if c in momentum.columns]]
                .sort_values("momentum_rank")
                .head(30),
                use_container_width=True,
                hide_index=True,
            )

    with c4:
        st.markdown('<div class="section-title">Turning Points significativos</div>', unsafe_allow_html=True)
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
# PÁGINA 3: RISK & ANOMALIES
# ============================================================
def risk_anomalies():
    st.title("Risk & Anomalies")
    st.caption("Análisis de anomalías, z-score, volatilidad, spreads y liquidez.")

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
        if not active.empty:
            active_view = active.copy()
            active_view["contract_short"] = active_view["contract_name"].apply(lambda x: short_text(x, 40))
            active_view["abs_z"] = active_view["z_score"].abs()
            make_bar(
                active_view.sort_values("abs_z", ascending=False).head(12).sort_values("abs_z"),
                x="abs_z",
                y="contract_short",
                title="Anomalías por z-score absoluto",
                hover_data=["market_name", "z_score", "current_price", "signal_strength"],
            )
        else:
            st.info("No hay anomalías activas en el último snapshot.")

    with c2:
        if not volatility.empty:
            vol30 = volatility[volatility["window_days"] == 30].copy()
            fig = px.scatter(
                vol30.dropna(subset=["volatility_score"]),
                x="current_price",
                y="volatility_score",
                size="price_range",
                hover_name="contract_name",
                hover_data=["market_name", "avg_price", "stddev_price"],
                title="Volatilidad vs precio actual",
            )
            fig.update_layout(
                height=420,
                margin=dict(l=10, r=10, t=50, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E5E7EB"),
                xaxis=dict(gridcolor="#263244"),
                yaxis=dict(gridcolor="#263244"),
            )
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns([1.1, 1])

    with c3:
        st.markdown('<div class="section-title">Tabla de anomalías</div>', unsafe_allow_html=True)
        if not anomalies.empty:
            view = anomalies.copy()
            view["abs_z"] = view["z_score"].abs()
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
        st.markdown('<div class="section-title">Spreads y liquidez</div>', unsafe_allow_html=True)
        if not spreads.empty:
            view = spreads.dropna(subset=["current_spread_yes"]).copy()
            view["contract_short"] = view["contract_name"].apply(lambda x: short_text(x, 38))
            make_bar(
                view.sort_values("current_spread_yes", ascending=False)
                .head(12)
                .sort_values("current_spread_yes"),
                x="current_spread_yes",
                y="contract_short",
                title="Mayor spread actual YES",
                hover_data=["market_name", "avg_spread_yes", "max_spread_yes"],
            )

    risk_level = "LOW"
    if active.shape[0] > 100 or (z_extreme is not None and z_extreme > 10):
        risk_level = "HIGH"
    elif active.shape[0] > 25 or (z_extreme is not None and z_extreme > 4):
        risk_level = "MEDIUM"

    st.markdown('<div class="section-title">Resumen ejecutivo de riesgo</div>', unsafe_allow_html=True)
    cls = "risk-high" if risk_level == "HIGH" else "risk-mid" if risk_level == "MEDIUM" else "risk-low"
    st.markdown(
        f"""
        <div class="risk-box">
            <div>Nivel estimado: <span class="{cls}">{risk_level}</span></div>
            <div class="small-note">
                Basado en anomalías activas, z-score extremo, volatilidad promedio y spreads actuales.
                Este resumen es una regla operativa, no una recomendación financiera.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PÁGINA 4: CONTRACT DETAIL
# ============================================================
def contract_detail():
    st.title("Contract Detail")
    st.caption("Vista de auditoría para revisar un contrato específico.")

    snapshot = safe_df("mart_market_snapshot", where_latest=True)
    movers = safe_df("mart_top_movers", where_latest=True)
    anomalies = safe_df("mart_anomaly_detection", where_latest=True)
    volatility = safe_df("mart_volatility_analysis", where_latest=True)
    spreads = safe_df("mart_spread_analysis", where_latest=True)
    rolling = query(f"SELECT * FROM {SCHEMA}.mart_rolling_averages")
    trends = query(f"SELECT * FROM {SCHEMA}.mart_price_trends")
    turning = query(f"SELECT * FROM {SCHEMA}.mart_turning_points")

    if snapshot.empty:
        st.warning("No hay datos para Contract Detail.")
        return

    contracts = snapshot.sort_values("last_trade_price", ascending=False)["contract_name"].dropna().unique().tolist()
    selected = st.sidebar.selectbox("Selecciona contrato", contracts, index=0)

    current = snapshot[snapshot["contract_name"] == selected].head(1)
    mover = movers[movers["contract_name"] == selected].head(1) if not movers.empty else pd.DataFrame()
    anom = anomalies[anomalies["contract_name"] == selected].head(1) if not anomalies.empty else pd.DataFrame()
    spread = spreads[spreads["contract_name"] == selected].head(1) if not spreads.empty else pd.DataFrame()
    vol = volatility[
        (volatility["contract_name"] == selected) & (volatility["window_days"] == 30)
    ].head(1) if not volatility.empty else pd.DataFrame()

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
                <b>Contrato:</b> {selected}<br>
                <b>Mercado:</b> {current.iloc[0]["market_name"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)

    with c1:
        t = (
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
        make_line(t, "snapshot_date", "avg_price", "Precio histórico promedio")

    with c2:
        r = rolling[rolling["contract_name"] == selected].sort_values("snapshot_date")
        if not r.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["close_price"], mode="lines+markers", name="Close"))
            fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["avg_7d"], mode="lines+markers", name="Avg 7d"))
            fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["avg_14d"], mode="lines+markers", name="Avg 14d"))
            fig.add_trace(go.Scatter(x=r["snapshot_date"], y=r["avg_30d"], mode="lines+markers", name="Avg 30d"))
            fig.update_layout(
                title="Close vs promedios móviles",
                height=430,
                margin=dict(l=10, r=10, t=50, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E5E7EB"),
                xaxis=dict(gridcolor="#263244"),
                yaxis=dict(gridcolor="#263244"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay rolling averages para este contrato.")

    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-title">Turning Points</div>', unsafe_allow_html=True)
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
            tp[[c for c in cols if c in tp.columns]]
            .sort_values("snapshot_date", ascending=False)
            .head(30),
            use_container_width=True,
            hide_index=True,
        )

    with c4:
        st.markdown('<div class="section-title">Riesgo y microestructura</div>', unsafe_allow_html=True)
        detail_rows = []

        if not anom.empty:
            a = anom.iloc[0]
            detail_rows.extend(
                [
                    {"Métrica": "Precio actual", "Valor": format_price(a.get("current_price"))},
                    {"Métrica": "Avg 30d", "Valor": format_price(a.get("avg_price_30d"))},
                    {"Métrica": "StdDev 30d", "Valor": format_price(a.get("stddev_price_30d"))},
                    {"Métrica": "Z-Score", "Valor": format_price(a.get("z_score"))},
                    {"Métrica": "Anomalía", "Valor": str(a.get("is_anomaly"))},
                    {"Métrica": "Signal Strength", "Valor": str(a.get("signal_strength"))},
                ]
            )

        if not spread.empty:
            s = spread.iloc[0]
            detail_rows.extend(
                [
                    {"Métrica": "Avg Spread YES", "Valor": format_price(s.get("avg_spread_yes"))},
                    {"Métrica": "Max Spread YES", "Valor": format_price(s.get("max_spread_yes"))},
                    {"Métrica": "Current Spread YES", "Valor": format_price(s.get("current_spread_yes"))},
                    {"Métrica": "Implied Volatility", "Valor": format_price(s.get("implied_volatility"))},
                ]
            )

        if not vol.empty:
            v = vol.iloc[0]
            detail_rows.extend(
                [
                    {"Métrica": "Window Days", "Valor": str(v.get("window_days"))},
                    {"Métrica": "Volatility Score", "Valor": format_price(v.get("volatility_score"))},
                    {"Métrica": "Price Range", "Valor": format_price(v.get("price_range"))},
                ]
            )

        st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)


# ============================================================
# ROUTER
# ============================================================
if page == "1. Executive Overview":
    executive_overview()
elif page == "2. Historical Trends":
    historical_trends()
elif page == "3. Risk & Anomalies":
    risk_anomalies()
else:
    contract_detail()
