# Crypto Analytics Dashboard

A sample Dash/Plotly application that visualizes synthetic cryptocurrency protocol analytics. The dashboard demonstrates how to build an interactive analytics interface with protocol-level and pool-level data.

## Features

- **Protocol-Level Analytics**: Visualize aggregate data across protocols (TVL, Fees, Revenue, etc.)
- **Pool-Level Analytics**: View granular data broken down by pool
- **Transaction Data**: Examine detailed transaction information
- **Interactive Filtering**: Apply filters by protocol, chain, time range, and metrics
- **Responsive Design**: Light-themed UI that works across devices

## Screenshots

[Note: Add screenshots here once the app is running]

## Installation

1. Clone this repository
2. Create and activate a virtual environment (recommended)
3. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Run the application:
```
python app.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:8050/
```

3. Interact with the dashboard:
   - Use the sidebar filters to select protocols, chains, date ranges, etc.
   - View various metrics in the cards at the top
   - Explore the interactive charts
   - View transaction data when the "Transactions" data type is selected

## Data Sources

This sample dashboard uses synthetic data generated in the `data.py` file. In a real-world application, you would replace these functions with actual data sources such as:

- Blockchain APIs (Etherscan, Subscan, etc.)
- Protocol-specific APIs or subgraphs
- Data aggregators (DefiLlama, Dune Analytics, etc.)

## Extending the Dashboard

To adapt this dashboard for real data:

1. Replace the data generation functions in `data.py` with calls to your data sources
2. Modify the metrics and dimensions to match your specific protocol needs
3. Enhance the UI with additional visualizations as needed

## Project Structure

- `app.py`: Main Dash application with layout and callbacks
- `data.py`: Data generation functions for synthetic protocol data
- `assets/style.css`: Custom styling for the dashboard
- `requirements.txt`: Python dependencies 