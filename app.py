import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# Import data generation functions
from data import generate_protocol_data, generate_pool_data, generate_transaction_data, get_current_metrics

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Create assets folder if it doesn't exist (for CSS file)
if not os.path.exists('assets'):
    os.makedirs('assets')

# Load initial data
protocol_data = generate_protocol_data()
pool_data = generate_pool_data()
transaction_data = generate_transaction_data(n_transactions=100)
current_metrics = get_current_metrics()

# Get unique values for filters
protocols = sorted(protocol_data['protocol'].unique())
chains = sorted(protocol_data['chain'].unique())
metrics = ['tvl', 'fees', 'revenue', 'expenses', 'volume']
versions = sorted(pool_data['version'].unique())

# Format currency values
def format_currency(value):
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

# Define the app layout
app.layout = html.Div(
    className="container",
    children=[
        # Sidebar
        html.Div(
            className="sidebar",
            children=[
                # Sidebar Header
                html.Div(
                    className="sidebar-header",
                    children=[
                        html.H1("Crypto Analytics", style={"fontSize": "24px", "marginBottom": "5px"}),
                        html.P("Dashboard v1.0", style={"color": "#6c757d", "marginTop": "0"})
                    ]
                ),
                
                # Protocol Filter
                html.Div(
                    className="sidebar-section",
                    children=[
                        html.H2("Protocol"),
                        dcc.Dropdown(
                            id="protocol-dropdown",
                            options=[{"label": p, "value": p} for p in protocols],
                            value=protocols[0],
                            multi=False
                        )
                    ]
                ),
                
                # Chain Filter
                html.Div(
                    className="sidebar-section",
                    children=[
                        html.H2("Chain"),
                        dcc.Dropdown(
                            id="chain-dropdown",
                            options=[{"label": c, "value": c} for c in chains],
                            value=chains,
                            multi=True
                        )
                    ]
                ),
                
                # Time Range Filter
                html.Div(
                    className="sidebar-section",
                    children=[
                        html.H2("Time Range"),
                        dcc.DatePickerRange(
                            id="date-picker",
                            start_date=protocol_data['date'].min(),
                            end_date=protocol_data['date'].max(),
                            display_format="MMM DD, YYYY"
                        )
                    ]
                ),
                
                # Metric Type
                html.Div(
                    className="sidebar-section",
                    children=[
                        html.H2("Metrics"),
                        dcc.Checklist(
                            id="metric-checklist",
                            options=[
                                {"label": " TVL", "value": "tvl"},
                                {"label": " Fees", "value": "fees"},
                                {"label": " Revenue", "value": "revenue"},
                                {"label": " Expenses", "value": "expenses"},
                                {"label": " Volume", "value": "volume"}
                            ],
                            value=["tvl", "fees", "revenue"],
                            labelStyle={"display": "block", "marginBottom": "8px"}
                        )
                    ]
                ),
                
                # Protocol Version
                html.Div(
                    className="sidebar-section",
                    children=[
                        html.H2("Version"),
                        dcc.Dropdown(
                            id="version-radio",
                            options=[{"label": v, "value": v} for v in versions] + [{"label": "All", "value": "all"}],
                            value="all",
                            clearable=False
                        )
                    ]
                ),
                
                # Data Type
                html.Div(
                    className="sidebar-section",
                    children=[
                        html.H2("Data Type"),
                        dcc.Dropdown(
                            id="data-type-radio",
                            options=[
                                {"label": "Protocol Level", "value": "protocol"},
                                {"label": "Pool Level", "value": "pool"},
                                {"label": "Transactions", "value": "transaction"}
                            ],
                            value="protocol",
                            clearable=False
                        )
                    ]
                ),
                
                # Apply Button
                html.Button("Apply Filters", id="apply-button", className="button", style={"width": "100%"})
            ]
        ),
        
        # Main Content
        html.Div(
            className="content",
            children=[
                # Header and Cards
                html.H1("Crypto Analytics Dashboard", style={"marginBottom": "15px", "fontSize": "24px"}),
                
                # Metric Cards
                html.Div(
                    className="card-container",
                    children=[
                        # TVL Card
                        html.Div(
                            className="metric-card",
                            children=[
                                html.Div(className="metric-title", children="Total Value Locked"),
                                html.Div(
                                    id="tvl-value",
                                    className="metric-value", 
                                    children=format_currency(current_metrics['total_tvl'])
                                )
                            ]
                        ),
                        # Fees Card
                        html.Div(
                            className="metric-card",
                            children=[
                                html.Div(className="metric-title", children="Total Fees"),
                                html.Div(
                                    id="fees-value",
                                    className="metric-value", 
                                    children=format_currency(current_metrics['total_fees'])
                                )
                            ]
                        ),
                        # Revenue Card
                        html.Div(
                            className="metric-card",
                            children=[
                                html.Div(className="metric-title", children="Total Revenue"),
                                html.Div(
                                    id="revenue-value",
                                    className="metric-value", 
                                    children=format_currency(current_metrics['total_revenue'])
                                )
                            ]
                        ),
                        # Volume Card
                        html.Div(
                            className="metric-card",
                            children=[
                                html.Div(className="metric-title", children="Total Volume"),
                                html.Div(
                                    id="volume-value",
                                    className="metric-value", 
                                    children=format_currency(current_metrics['total_volume'])
                                )
                            ]
                        ),
                        # Active Chains Card
                        html.Div(
                            className="metric-card",
                            children=[
                                html.Div(className="metric-title", children="Active Chains"),
                                html.Div(
                                    id="chains-value",
                                    className="metric-value", 
                                    children=str(current_metrics['active_chains'])
                                )
                            ]
                        ),
                        # Active Protocols Card
                        html.Div(
                            className="metric-card",
                            children=[
                                html.Div(className="metric-title", children="Active Protocols"),
                                html.Div(
                                    id="protocols-value",
                                    className="metric-value", 
                                    children="1"
                                )
                            ]
                        )
                    ]
                ),
                
                # Graphs Section with Grid Layout
                html.Div(
                    className="charts-section",
                    children=[
                        # Graph 1: Protocol Metrics Over Time (full width)
                        html.Div(
                            className="graph-container",
                            children=[
                                html.Div(className="graph-title", children="Protocol Metrics Over Time"),
                                dcc.Graph(id="time-series-graph", style={"height": "300px"})
                            ]
                        ),
                        
                        # Graph 2: Distribution by Chain
                        html.Div(
                            className="graph-container",
                            children=[
                                html.Div(className="graph-title", children="Distribution by Chain"),
                                dcc.Graph(id="chain-distribution-graph", style={"height": "250px"})
                            ]
                        ),
                        
                        # Graph 3: Protocol Comparison
                        html.Div(
                            className="graph-container",
                            children=[
                                html.Div(className="graph-title", children="Chain Comparison"),
                                dcc.Graph(id="protocol-comparison-graph", style={"height": "250px"})
                            ]
                        )
                    ]
                ),
                
                # Transaction Table
                html.Div(
                    id="transaction-table-container",
                    className="table-container",
                    children=[
                        html.Div(className="graph-title", children="Recent Transactions"),
                        dash_table.DataTable(
                            id="transaction-table",
                            columns=[
                                {"name": "Time", "id": "timestamp"},
                                {"name": "Protocol", "id": "protocol"},
                                {"name": "Chain", "id": "chain"},
                                {"name": "Wallet", "id": "wallet_address"},
                                {"name": "Action", "id": "action"},
                                {"name": "Amount (USD)", "id": "amount_usd"},
                                {"name": "Gas Fee (USD)", "id": "gas_fee_usd"}
                            ],
                            data=transaction_data.sort_values("timestamp", ascending=False).head(10).to_dict("records"),
                            style_cell={
                                'textAlign': 'left',
                                'padding': '5px 10px',
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'fontFamily': "'Segoe UI', sans-serif",
                                'fontSize': 12
                            },
                            style_header={
                                'backgroundColor': '#f8f9fa',
                                'fontWeight': 'bold',
                                'borderBottom': '1px solid #e9ecef',
                                'fontSize': 12,
                                'height': 'auto',
                                'padding': '5px 10px'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f8f9fa'
                                }
                            ],
                            page_size=5,
                            style_as_list_view=True,
                            style_table={'overflowX': 'auto', 'maxHeight': '250px'}
                        )
                    ]
                )
            ]
        )
    ]
)

# Callback for updating time series graph
@app.callback(
    Output("time-series-graph", "figure"),
    [Input("apply-button", "n_clicks")],
    [
        State("protocol-dropdown", "value"),
        State("chain-dropdown", "value"),
        State("date-picker", "start_date"),
        State("date-picker", "end_date"),
        State("metric-checklist", "value"),
        State("data-type-radio", "value")
    ]
)
def update_time_series(n_clicks, protocol, chains, start_date, end_date, metrics, data_type):
    # Choose dataset based on data type
    if data_type == "protocol":
        df = protocol_data.copy()
        title = "Protocol Metrics Over Time"
    else:
        df = pool_data.copy()
        title = "Pool Metrics Over Time"
    
    # Apply filters
    df = df[df["protocol"] == protocol]
    df = df[df["chain"].isin(chains)]
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    
    # Group by date and aggregate selected metrics
    grouped_df = df.groupby("date")[metrics].sum().reset_index()
    
    # Create figure
    fig = go.Figure()
    
    # Color map for different metrics
    colors = {
        'tvl': '#0066cc',
        'fees': '#5cb85c',
        'revenue': '#f0ad4e',
        'expenses': '#d9534f',
        'volume': '#5bc0de'
    }
    
    for metric in metrics:
        fig.add_trace(
            go.Scatter(
                x=grouped_df["date"],
                y=grouped_df[metric],
                mode="lines",
                name=metric.capitalize(),
                line=dict(color=colors.get(metric, '#0066cc'), width=2)
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        height=300
    )
    
    # Format y-axis to be more readable
    fig.update_yaxes(tickformat="$.2s")
    
    return fig

# Callback for updating chain distribution graph
@app.callback(
    Output("chain-distribution-graph", "figure"),
    [Input("apply-button", "n_clicks")],
    [
        State("protocol-dropdown", "value"),
        State("chain-dropdown", "value"),
        State("date-picker", "start_date"),
        State("date-picker", "end_date"),
        State("metric-checklist", "value"),
        State("data-type-radio", "value")
    ]
)
def update_chain_distribution(n_clicks, protocol, chains, start_date, end_date, metrics, data_type):
    # Choose dataset based on data type
    if data_type == "protocol":
        df = protocol_data.copy()
    else:
        df = pool_data.copy()
    
    # Apply filters
    df = df[df["protocol"] == protocol]
    df = df[df["chain"].isin(chains)]
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    
    # Use the first metric in the list by default
    selected_metric = metrics[0] if metrics else "tvl"
    
    # Group by chain and aggregate selected metric
    chain_data = df.groupby("chain")[selected_metric].sum().reset_index()
    
    # Create figure
    fig = px.pie(
        chain_data,
        values=selected_metric,
        names="chain",
        title=f"{selected_metric.capitalize()} Distribution",
        hole=0.4,  # Make it a donut chart for more compact look
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=250,
        showlegend=True
    )
    
    # Add percentage labels
    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        insidetextfont=dict(size=10)
    )
    
    return fig

# Callback for updating protocol comparison graph
@app.callback(
    Output("protocol-comparison-graph", "figure"),
    [Input("apply-button", "n_clicks")],
    [
        State("protocol-dropdown", "value"),
        State("chain-dropdown", "value"),
        State("date-picker", "start_date"),
        State("date-picker", "end_date"),
        State("metric-checklist", "value"),
        State("data-type-radio", "value"),
        State("version-radio", "value")
    ]
)
def update_protocol_comparison(n_clicks, protocol, chains, start_date, end_date, metrics, data_type, version):
    # Choose dataset based on data type
    if data_type == "protocol":
        df = protocol_data.copy()
    else:
        df = pool_data.copy()
        if version != "all":
            df = df[df["version"] == version]
    
    # Apply filters - only filter by the selected protocol
    df = df[df["protocol"] == protocol]
    df = df[df["chain"].isin(chains)]
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    
    # Use the first metric in the list by default
    selected_metric = metrics[0] if metrics else "tvl"
    
    # For protocol comparison with single protocol selection, show comparison by chains
    # Group by chain and aggregate selected metric
    comparison_data = df.groupby("chain")[selected_metric].sum().reset_index()
    
    # Sort data by value for better visualization
    comparison_data = comparison_data.sort_values(selected_metric, ascending=False)
    
    # Create figure - use horizontal bar chart for compactness
    fig = px.bar(
        comparison_data,
        y="chain",
        x=selected_metric,
        title=f"{selected_metric.capitalize()} by Chain",
        color=selected_metric,
        color_continuous_scale="Blues",
        text=selected_metric
    )
    
    # Format text labels
    fig.update_traces(
        texttemplate='%{text:$.2s}', 
        textposition='outside'
    )
    
    fig.update_layout(
        yaxis_title="",
        xaxis_title="",
        margin=dict(l=0, r=10, t=30, b=0),
        template="plotly_white",
        coloraxis_showscale=False,
        showlegend=False
    )
    
    # Add percentage text
    total = comparison_data[selected_metric].sum()
    for i, chain in enumerate(comparison_data["chain"]):
        value = comparison_data.iloc[i][selected_metric]
        percentage = (value / total) * 100
        fig.add_annotation(
            x=value,
            y=chain,
            text=f"{percentage:.1f}%",
            showarrow=False,
            xshift=45,
            font=dict(size=9)
        )
    
    return fig

# Callback for updating transaction table
@app.callback(
    Output("transaction-table", "data"),
    [Input("apply-button", "n_clicks")],
    [
        State("protocol-dropdown", "value"),
        State("chain-dropdown", "value"),
        State("data-type-radio", "value")
    ]
)
def update_transaction_table(n_clicks, protocol, chains, data_type):
    if data_type != "transaction":
        return []
    
    # Filter transactions
    df = transaction_data.copy()
    df = df[df["protocol"] == protocol]
    df = df[df["chain"].isin(chains)]
    
    # Format timestamp
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Format amount and gas fee
    df["amount_usd"] = df["amount_usd"].apply(lambda x: f"${x:.2f}")
    df["gas_fee_usd"] = df["gas_fee_usd"].apply(lambda x: f"${x:.2f}")
    
    # Shorten wallet address for display
    df["wallet_address"] = df["wallet_address"].apply(lambda x: x[:6] + "..." + x[-4:])
    
    return df.sort_values("timestamp", ascending=False).head(10).to_dict("records")

# Callback for updating the visibility of transaction table
@app.callback(
    Output("transaction-table-container", "style"),
    [Input("data-type-radio", "value")]
)
def toggle_transaction_table(data_type):
    if data_type == "transaction":
        return {"display": "block"}
    else:
        return {"display": "none"}

# Callback for updating metric cards
@app.callback(
    [
        Output("tvl-value", "children"),
        Output("fees-value", "children"),
        Output("revenue-value", "children"),
        Output("volume-value", "children"),
        Output("chains-value", "children"),
        Output("protocols-value", "children")
    ],
    [Input("apply-button", "n_clicks")],
    [
        State("protocol-dropdown", "value"),
        State("chain-dropdown", "value"),
        State("date-picker", "end_date")
    ]
)
def update_metric_cards(n_clicks, protocol, chains, end_date):
    # Filter data
    df = protocol_data.copy()
    df = df[df["protocol"] == protocol]
    df = df[df["chain"].isin(chains)]

    # Get latest date data
    df_before_or_equal = df[df["date"] <= end_date]
    latest_valid_date = df_before_or_equal["date"].max()
    latest_data = df[df["date"] == latest_valid_date]
    
    # Calculate metrics
    tvl = latest_data["tvl"].sum()
    fees = latest_data["fees"].sum()
    revenue = latest_data["revenue"].sum()
    volume = latest_data["volume"].sum()
    active_chains = len(latest_data["chain"].unique())
    
    return (
        format_currency(tvl),
        format_currency(fees),
        format_currency(revenue),
        format_currency(volume),
        str(active_chains),
        "1"  # Only one protocol is selected
    )

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True) 