import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, dash_table, dcc, html


SCHEMA = "main_marts"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WINDOWS_WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
LINUX_WAREHOUSE_DIR = Path("/mnt/d/mineria data/airflow/data/warehouse")

DEFAULT_DB_CANDIDATES = [
    LINUX_WAREHOUSE_DIR / "predictit_bi.duckdb",
    LINUX_WAREHOUSE_DIR / "predictit.duckdb",
    WINDOWS_WAREHOUSE_DIR / "predictit_bi.duckdb",
    WINDOWS_WAREHOUSE_DIR / "predictit.duckdb",
]


def resolve_db_path() -> str:
    env_path = os.getenv("PREDICTIT_DUCKDB_PATH")
    if env_path:
        return env_path
    return str(next((path for path in DEFAULT_DB_CANDIDATES if path.exists()), DEFAULT_DB_CANDIDATES[0]))


DB_PATH = resolve_db_path()


def query(sql: str, params=None) -> pd.DataFrame:
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(sql, params or []).fetchdf()


def latest_df(table: str) -> pd.DataFrame:
    latest = query(f"SELECT MAX(extraction_ts) AS extraction_ts FROM {SCHEMA}.{table}")
    if latest.empty or pd.isna(latest.loc[0, "extraction_ts"]):
        return pd.DataFrame()
    return query(f"SELECT * FROM {SCHEMA}.{table} WHERE extraction_ts = ?", [latest.loc[0, "extraction_ts"]])


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "snapshot": latest_df("mart_market_snapshot"),
        "movers": latest_df("mart_top_movers"),
        "anomalies": latest_df("mart_anomaly_detection"),
        "spreads": latest_df("mart_spread_analysis"),
        "volatility": latest_df("mart_volatility_analysis"),
    }


DATA = load_data()


def short_text(value, max_len=42):
    if pd.isna(value):
        return ""
    value = str(value)
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def format_price(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.3f}"


def format_pct(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def latest_label(df: pd.DataFrame) -> str:
    if df.empty or "extraction_ts" not in df.columns:
        return "N/A"
    return pd.to_datetime(df["extraction_ts"].max()).strftime("%d/%m/%Y %H:%M")


def filter_df(df: pd.DataFrame, market: str, contract: str) -> pd.DataFrame:
    if df.empty:
        return df
    filtered = df.copy()
    if market != "Todos" and "market_name" in filtered.columns:
        filtered = filtered[filtered["market_name"] == market]
    if contract != "Todos" and "contract_name" in filtered.columns:
        filtered = filtered[filtered["contract_name"] == contract]
    return filtered


def kpi_card(icon, label, value, note, color):
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(icon, className="kpi-icon", style={"color": color}),
            html.Div(
                [
                    html.Div(label, className="kpi-label", style={"color": color}),
                    html.Div(value, className="kpi-value"),
                    html.Div(note, className="kpi-note"),
                ]
            ),
        ],
    )


def panel(title, subtitle=None, children=None):
    return html.Div(
        className="panel",
        children=[
            html.Div(
                [
                    html.Span(title, className="panel-title"),
                    html.Span(f" {subtitle}", className="panel-subtitle") if subtitle else None,
                ],
                className="panel-heading",
            ),
            html.Div(children if children is not None else [], className="panel-body"),
        ],
    )


def contract_options_for_market(market: str):
    snapshot = DATA["snapshot"]
    options = [{"label": "Todos", "value": "Todos"}]
    if snapshot.empty:
        return options

    filtered = snapshot
    if market and market != "Todos":
        filtered = filtered[filtered["market_name"] == market]

    contracts = filtered["contract_name"].dropna().sort_values().unique()
    return options + [{"label": value, "value": value} for value in contracts]


def data_table(df: pd.DataFrame, height=300):
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_action="none",
        fixed_rows={"headers": True},
        style_table={"height": height, "overflowY": "auto"},
        style_header={
            "backgroundColor": "#ffffff",
            "borderBottom": "1px solid #d7dce3",
            "fontWeight": "700",
            "color": "#111827",
        },
        style_cell={
            "fontFamily": "Inter, Arial, sans-serif",
            "fontSize": "13px",
            "padding": "8px 8px",
            "border": "0",
            "borderBottom": "1px solid #edf0f4",
            "whiteSpace": "normal",
            "height": "auto",
            "color": "#111827",
            "backgroundColor": "#ffffff",
        },
        style_cell_conditional=[
            {"if": {"column_id": "Contrato"}, "width": "30%", "textAlign": "left"},
            {"if": {"column_id": "Mercado"}, "width": "42%", "textAlign": "left"},
            {"if": {"column_id": "Precio Actual"}, "width": "14%"},
            {"if": {"column_id": "Cambio % (24h)"}, "width": "14%"},
        ],
    )


def plot_layout(fig, height=300):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=10, b=36),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827", size=12),
        xaxis=dict(gridcolor="#e6eaf0", zeroline=False),
        yaxis=dict(gridcolor="#e6eaf0", zeroline=False),
        legend=dict(font=dict(size=12), orientation="v"),
    )
    return fig


def blank_figure(message="Sin datos"):
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#64748b"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return plot_layout(fig)


snapshot = DATA["snapshot"]
market_options = [{"label": "Todos", "value": "Todos"}]
contract_options = [{"label": "Todos", "value": "Todos"}]
if not snapshot.empty:
    market_options += [{"label": value, "value": value} for value in sorted(snapshot["market_name"].dropna().unique())]
    contract_options += [
        {"label": value, "value": value} for value in sorted(snapshot["contract_name"].dropna().unique())
    ]


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Panel Analitico PredictIt")
server = app.server

app.layout = html.Div(
    className="app-shell",
    children=[
        html.Aside(
            className="sidebar",
            children=[
                html.Div([html.Span(), html.Span(), html.Span(), html.Span()], className="logo-bars"),
                html.Nav(
                    [
                        html.Div("⌂  Overview", className="nav-item active"),
                        html.Div("↗  Trends", className="nav-item"),
                        html.Div("△  Risk & Anomalies", className="nav-item"),
                        html.Div("▤  Contract Detail", className="nav-item"),
                    ]
                ),
                html.Div(
                    className="sidebar-filters",
                    children=[
                        html.Div("Filtros Globales", className="filter-title"),
                        html.Div("Usa los filtros superiores para mercado y contrato.", className="filter-note"),
                    ],
                ),
            ],
        ),
        html.Main(
            className="content",
            children=[
                html.Div(
                    className="topbar",
                    children=[
                        html.Div(
                            [
                                html.H1("Panel Analitico PredictIt"),
                                html.Div("Resumen Ejecutivo", className="subtitle"),
                            ]
                        ),
                        html.Div(
                            className="top-filters",
                            children=[
                                html.Div([html.Label("Fecha"), dcc.Input(value=latest_label(snapshot)[:10], readOnly=True)]),
                                html.Div([html.Label("Mercado"), dcc.Dropdown(id="market-filter", options=market_options, value="Todos", clearable=False)]),
                                html.Div([html.Label("Contrato"), dcc.Dropdown(id="contract-filter", options=contract_options, value="Todos", clearable=False)]),
                                html.Div(
                                    [
                                        html.Label("Ultima actualizacion"),
                                        html.Strong(latest_label(snapshot)),
                                    ],
                                    className="last-refresh",
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(id="dashboard-body"),
            ],
        ),
    ],
)


@app.callback(
    Output("contract-filter", "options"),
    Output("contract-filter", "value"),
    Input("market-filter", "value"),
    State("contract-filter", "value"),
)
def update_contracts(selected_market, selected_contract):
    options = contract_options_for_market(selected_market)
    valid_values = {option["value"] for option in options}
    value = selected_contract if selected_contract in valid_values else "Todos"
    return options, value


@app.callback(
    Output("dashboard-body", "children"),
    Input("market-filter", "value"),
    Input("contract-filter", "value"),
)
def render_dashboard(selected_market, selected_contract):
    snapshot_view = filter_df(DATA["snapshot"], selected_market, selected_contract)
    movers_view = filter_df(DATA["movers"], selected_market, selected_contract)
    anomalies_view = filter_df(DATA["anomalies"], selected_market, selected_contract)
    spreads_view = filter_df(DATA["spreads"], selected_market, selected_contract)

    if snapshot_view.empty:
        return dbc.Alert("No hay datos para los filtros seleccionados.", color="warning")

    markets = snapshot_view["market_id"].nunique()
    contracts = snapshot_view["contract_id"].nunique()
    avg_price = snapshot_view["last_trade_price"].mean()
    active_anomalies = (
        anomalies_view[anomalies_view["is_anomaly"] == True].shape[0] if not anomalies_view.empty else 0
    )

    max_gain_row = movers_view.sort_values("change_pct", ascending=False).head(1)
    max_loss_row = movers_view.sort_values("change_pct", ascending=True).head(1)
    max_gain = max_gain_row["change_pct"].iloc[0] if not max_gain_row.empty else None
    max_loss = max_loss_row["change_pct"].iloc[0] if not max_loss_row.empty else None
    max_gain_name = short_text(max_gain_row["contract_name"].iloc[0], 18) if not max_gain_row.empty else "N/A"
    max_loss_name = short_text(max_loss_row["contract_name"].iloc[0], 18) if not max_loss_row.empty else "N/A"

    movers_table = pd.DataFrame(columns=["Contrato", "Mercado", "Precio Actual", "Cambio % (24h)"])
    if not movers_view.empty:
        movers_table = movers_view.sort_values("change_pct", ascending=False).head(6).copy()
        movers_table["Contrato"] = movers_table["contract_name"].apply(lambda x: short_text(x, 26))
        movers_table["Mercado"] = movers_table["market_name"].apply(lambda x: short_text(x, 35))
        movers_table["Precio Actual"] = movers_table["price_now"].map(format_price)
        movers_table["Cambio % (24h)"] = movers_table["change_pct"].map(format_pct)
        movers_table = movers_table[["Contrato", "Mercado", "Precio Actual", "Cambio % (24h)"]]

    leaders = (
        snapshot_view.groupby("market_name", as_index=False)
        .agg(
            contracts=("contract_id", "nunique"),
            avg_price=("last_trade_price", "mean"),
        )
        .sort_values("contracts", ascending=False)
        .head(8)
    )
    if leaders.empty:
        leaders_fig = blank_figure()
    else:
        leaders["market_short"] = leaders["market_name"].apply(lambda x: short_text(x, 34))
        leaders_fig = px.bar(
            leaders.sort_values("contracts"),
            x="contracts",
            y="market_short",
            orientation="h",
            text="contracts",
            hover_data=["market_name", "avg_price"],
            color_discrete_sequence=["#1266d6"],
        )
        leaders_fig.update_traces(textposition="outside", cliponaxis=False)
        leaders_fig.update_xaxes(title="Contratos", range=[0, max(1.0, leaders["contracts"].max() * 1.18)])
        leaders_fig.update_yaxes(title="")
        leaders_fig = plot_layout(leaders_fig, 315)

    market_dist = (
        snapshot_view.groupby("market_name", as_index=False)
        .agg(contracts=("contract_id", "nunique"))
        .sort_values("contracts", ascending=False)
    )
    if market_dist.empty:
        pie_fig = blank_figure()
    else:
        top_dist = market_dist.head(5).copy()
        others = market_dist.iloc[5:]["contracts"].sum()
        if others:
            top_dist = pd.concat(
                [pd.DataFrame([{"market_name": "Otros mercados", "contracts": others}]), top_dist],
                ignore_index=True,
            )
        top_dist["market_label"] = top_dist["market_name"].apply(lambda x: short_text(x, 24))
        pie_fig = px.pie(
            top_dist,
            names="market_label",
            values="contracts",
            hole=0.52,
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data=["market_name"],
        )
        pie_fig.update_traces(textinfo="percent", textposition="inside", insidetextorientation="radial")
        pie_fig.add_annotation(
            text=f"<b>{contracts:,}</b><br>Total",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=22, color="#111827"),
        )
        pie_fig = plot_layout(pie_fig, 315)
        pie_fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5, font=dict(size=10)),
            margin=dict(l=5, r=5, t=0, b=55),
        )

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
    market_snapshot["Mercado"] = market_snapshot["market_name"].apply(lambda x: short_text(x, 42))
    market_snapshot["Precio Prom."] = market_snapshot["Precio_Prom"].map(format_price)
    market_snapshot["Spread Prom."] = market_snapshot["Spread_Prom"].map(format_price)
    market_snapshot = market_snapshot[["Mercado", "Contratos", "Precio Prom.", "Spread Prom."]]

    anom_table = pd.DataFrame(columns=["Contrato", "Mercado", "Z-Score", "Fuerza"])
    if not anomalies_view.empty:
        active = anomalies_view[anomalies_view["is_anomaly"] == True].copy()
        if not active.empty:
            active["Contrato"] = active["contract_name"].apply(lambda x: short_text(x, 24))
            active["Mercado"] = active["market_name"].apply(lambda x: short_text(x, 32))
            active["Z-Score"] = active["z_score"].map(lambda x: f"{x:+.2f}" if not pd.isna(x) else "N/A")
            active["Fuerza"] = active["signal_strength"].fillna("N/A")
            anom_table = active.sort_values("z_score", key=lambda s: s.abs(), ascending=False).head(6)
            anom_table = anom_table[["Contrato", "Mercado", "Z-Score", "Fuerza"]]

    spread_fig = blank_figure()
    if not spreads_view.empty:
        top_spreads = spreads_view.dropna(subset=["current_spread_yes"]).copy()
        if not top_spreads.empty:
            top_spreads["contract_short"] = top_spreads["contract_name"].apply(lambda x: short_text(x, 12))
            top_spreads = top_spreads.sort_values("current_spread_yes", ascending=False).head(5)
            spread_fig = px.bar(
                top_spreads,
                x="contract_short",
                y="current_spread_yes",
                text="current_spread_yes",
                color_discrete_sequence=["#1266d6"],
            )
            spread_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            spread_fig.update_xaxes(title="", tickangle=-25)
            spread_fig.update_yaxes(title="Spread prom.", range=[0, max(1.0, top_spreads["current_spread_yes"].max() * 1.2)])
            spread_fig = plot_layout(spread_fig, 280)
            spread_fig.update_layout(margin=dict(l=10, r=10, t=5, b=72))

    return [
        html.Div(
            className="kpi-grid",
            children=[
                kpi_card("◎", "Mercados Totales", f"{markets:,}", "Mercados activos", "#1266d6"),
                kpi_card("▤", "Contratos Totales", f"{contracts:,}", "Contratos activos", "#166534"),
                kpi_card("↗", "Precio Promedio", format_price(avg_price), "Promedio actual", "#6d28d9"),
                kpi_card("▲", "Mayor Subida (24h)", format_pct(max_gain), max_gain_name, "#168a2f"),
                kpi_card("▼", "Mayor Bajada (24h)", format_pct(max_loss), max_loss_name, "#dc1f1f"),
                kpi_card("!", "Anomalias Activas", f"{active_anomalies:,}", "Senales activas", "#f97316"),
            ],
        ),
        html.Div(
            className="dashboard-grid top-grid",
            children=[
                panel("Mayores Movimientos", "(24h)", data_table(movers_table, 280)),
                panel("Lideres por Mercado", "(Top mercados por # contratos)", dcc.Graph(figure=leaders_fig, config={"displayModeBar": False})),
                panel("Distribucion de Contratos por Mercado", children=dcc.Graph(figure=pie_fig, config={"displayModeBar": False})),
            ],
        ),
        html.Div(
            className="dashboard-grid bottom-grid",
            children=[
                panel("Resumen del Mercado", "(tiempo real)", data_table(market_snapshot, 260)),
                panel("Anomalias Activas", "(Senales de Alerta)", data_table(anom_table, 260)),
                panel("Spreads Mas Amplios", children=dcc.Graph(figure=spread_fig, config={"displayModeBar": False})),
            ],
        ),
    ]


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                background: #f6f7f9;
                color: #111827;
                font-family: Inter, Arial, sans-serif;
            }

            .app-shell {
                display: grid;
                grid-template-columns: 220px minmax(0, 1fr);
                min-height: 100vh;
            }

            .sidebar {
                background: linear-gradient(180deg, #101820 0%, #121a22 55%, #0d131a 100%);
                color: #ffffff;
                padding: 0;
                position: sticky;
                top: 0;
                height: 100vh;
                box-shadow: 2px 0 8px rgba(0,0,0,.14);
            }

            .logo-bars {
                height: 96px;
                display: flex;
                align-items: end;
                gap: 5px;
                padding: 0 0 22px 42px;
                border-bottom: 1px solid rgba(255,255,255,.1);
            }

            .logo-bars span {
                width: 11px;
                background: #f5b700;
                display: block;
            }

            .logo-bars span:nth-child(1) { height: 18px; }
            .logo-bars span:nth-child(2) { height: 30px; }
            .logo-bars span:nth-child(3) { height: 43px; }
            .logo-bars span:nth-child(4) { height: 58px; }

            .nav-item {
                margin: 14px 10px;
                padding: 13px 14px;
                border-radius: 8px;
                font-weight: 700;
                color: #f8fafc;
            }

            .nav-item.active {
                background: #2b323a;
                color: #f5d000;
                border-left: 4px solid #f5b700;
            }

            .sidebar-filters {
                position: absolute;
                left: 8px;
                right: 8px;
                bottom: 76px;
                border: 1px solid rgba(255,255,255,.15);
                border-radius: 8px;
                padding: 14px;
            }

            .filter-title {
                color: #f5d000;
                font-weight: 800;
                margin-bottom: 12px;
            }

            .filter-note {
                color: #cbd5e1;
                font-size: 13px;
                line-height: 1.35;
            }

            .sidebar label {
                color: #ffffff;
                font-size: 13px;
                margin: 9px 0 4px 0;
            }

            .dark-dropdown .Select-control,
            .dark-dropdown .Select-menu-outer,
            .dark-dropdown .Select-value {
                background: #171f28 !important;
                color: #ffffff !important;
                border-color: #46515f !important;
            }

            .content {
                padding: 22px 20px 28px 20px;
                min-width: 0;
            }

            .topbar {
                display: grid;
                grid-template-columns: minmax(300px, 1fr) minmax(520px, 0.95fr);
                gap: 20px;
                align-items: start;
                border-bottom: 1px solid #dfe3e8;
                padding-bottom: 16px;
                margin-bottom: 16px;
            }

            h1 {
                font-size: 30px;
                line-height: 1.1;
                margin: 0 0 7px 0;
                font-weight: 900;
                color: #0f172a;
            }

            .subtitle {
                font-size: 17px;
                color: #3f4651;
            }

            .top-filters {
                display: grid;
                grid-template-columns: .9fr 1fr 1.1fr 1.05fr;
                gap: 14px;
                align-items: end;
            }

            .top-filters label {
                display: block;
                font-size: 13px;
                color: #111827;
                margin-bottom: 4px;
            }

            .top-filters input {
                height: 36px;
                border: 1px solid #d7dce3;
                border-radius: 6px;
                padding: 0 10px;
                width: 100%;
                background: #ffffff;
            }

            .last-refresh strong {
                display: block;
                font-size: 14px;
                margin-top: 5px;
            }

            .kpi-grid {
                display: grid;
                grid-template-columns: repeat(6, minmax(0, 1fr));
                gap: 14px;
                margin-bottom: 16px;
            }

            .kpi-card {
                background: #ffffff;
                border: 1px solid #d9dde4;
                border-radius: 8px;
                min-height: 116px;
                padding: 16px 14px;
                display: flex;
                gap: 13px;
                align-items: center;
                box-shadow: 0 1px 2px rgba(15,23,42,.06);
            }

            .kpi-icon {
                min-width: 42px;
                text-align: center;
                font-size: 42px;
                font-weight: 900;
                line-height: 1;
            }

            .kpi-label {
                font-weight: 900;
                font-size: 14px;
                margin-bottom: 5px;
            }

            .kpi-value {
                color: #050505;
                font-size: 30px;
                font-weight: 900;
                line-height: 1.05;
            }

            .kpi-note {
                color: #222831;
                font-size: 13px;
                margin-top: 5px;
            }

            .dashboard-grid {
                display: grid;
                grid-template-columns: 1.05fr 1fr 1.05fr;
                gap: 14px;
                margin-bottom: 14px;
            }

            .panel {
                background: #ffffff;
                border: 1px solid #d9dde4;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 2px rgba(15,23,42,.05);
            }

            .panel-heading {
                padding: 12px 14px 4px 14px;
                min-height: 46px;
            }

            .panel-title {
                color: #111827;
                font-weight: 900;
                font-size: 17px;
            }

            .panel-subtitle {
                color: #343a44;
                font-size: 14px;
            }

            .panel-body {
                padding: 0 12px 12px 12px;
            }

            @media (max-width: 1260px) {
                .app-shell { grid-template-columns: 190px minmax(0, 1fr); }
                .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
                .dashboard-grid { grid-template-columns: 1fr; }
                .topbar { grid-template-columns: 1fr; }
            }

            @media (max-width: 760px) {
                .app-shell { display: block; }
                .sidebar { position: relative; height: auto; }
                .sidebar-filters { position: static; margin: 16px 8px; }
                .kpi-grid { grid-template-columns: 1fr; }
                .top-filters { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
