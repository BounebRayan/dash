import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta,date

# Slug mapping: protocol name -> DefiLlama slug
PROTOCOL_SLUGS = {
    'Aave': 'aave',
    'Drift': 'drift',
    'Fluid': 'fluid',
    'Aerodrome': 'aerodrome',
    'Ethena': 'ethena',
}

CHAINS_OF_INTEREST = ['Ethereum', 'Polygon', 'Arbitrum', 'OP Mainnet', 'Base','Solana']

def generate_date_range(days=180):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return pd.date_range(start=start_date, end=end_date, freq='D')

def fetch_protocol_tvl(slug):
    url = f"https://api.llama.fi/protocol/{slug}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        print(f"Failed to fetch TVL for {slug}")
        return None

def fetch_protocol_fees(slug):
    url = f"https://api.llama.fi/summary/fees/{slug}?dataType=dailyFees"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        print(f"Failed to fetch fees for {slug}")
        return None

def fetch_protocol_revenue(slug):
    url = f"https://api.llama.fi/summary/fees/{slug}?dataType=dailyRevenue"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        print(f"Failed to fetch fees for {slug}")
        return None
    
def fetch_protocol_volume(slug):
    url = f"https://api.llama.fi/summary/dexs/{slug}?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=false&dataType=dailyVolume"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        print(f"Failed to fetch volume for {slug}")
        return None
       
    
def tvl_to_df(tvl_data, chain):
    try:
        tvl_series = tvl_data.get("chainTvls", {}).get(chain, {}).get("tvl", [])
        return pd.DataFrame({
            "date": pd.to_datetime([e["date"] for e in tvl_series], unit='s'),  # datetime64[ns]
            "tvl": [e.get("totalLiquidityUSD", np.nan) for e in tvl_series]
        })
    except Exception as e:
        print(f"Error in tvl_to_df: {e}")
        return pd.DataFrame()




def fees_to_df(fees_data, chain):
    try:
        daily_data = fees_data.get("totalDataChartBreakdown", [])
        parsed = []

        for entry in daily_data:
            timestamp, breakdown = entry
            chain_data = breakdown.get(chain.lower())

            if not chain_data:
                continue

            # Sum all components (e.g. Fluid Lending, Fluid DEX)
            total_fees = sum(chain_data.values())
            parsed.append({
                "date": pd.to_datetime(timestamp, unit="s"),
                "fees": total_fees
            })

        return pd.DataFrame(parsed)
    except Exception as e:
        print(f"Error in fees_to_df for chain {chain}: {e}")
        return pd.DataFrame()


def revenue_to_df(fees_data, chain):
    try:
        daily_data = fees_data.get("totalDataChartBreakdown", [])
        parsed = []

        for entry in daily_data:
            timestamp, breakdown = entry
            chain_data = breakdown.get(chain.lower())

            if not chain_data:
                continue

            # Sum all components (e.g. Fluid Lending, Fluid DEX)
            total_revenue = sum(chain_data.values())
            parsed.append({
                "date": pd.to_datetime(timestamp, unit="s"),
                "revenue": total_revenue
            })

        return pd.DataFrame(parsed)
    except Exception as e:
        print(f"Error in fees_to_df for chain {chain}: {e}")
        return pd.DataFrame()

def volume_to_df(volume_data, chain):
    try:
        daily_data = volume_data.get("totalDataChartBreakdown", [])
        parsed = []

        for entry in daily_data:
            timestamp, breakdown = entry
            chain_data = breakdown.get(chain.lower())

            if not chain_data:
                continue

            # Sum all components (e.g. Fluid Lending, Fluid DEX)
            total_volume = sum(chain_data.values())
            parsed.append({
                "date": pd.to_datetime(timestamp, unit="s"),
                "volume": total_volume
            })

        return pd.DataFrame(parsed)
    except Exception as e:
        print(f"Error in fees_to_df for chain {chain}: {e}")
        return pd.DataFrame()

def generate_protocol_data(days=180):
    date_range = generate_date_range(days)
    base_df = pd.DataFrame({"date": date_range})

    all_data = []

    for protocol_name, slug in PROTOCOL_SLUGS.items():
        tvl_raw = fetch_protocol_tvl(slug)
        fees_raw = fetch_protocol_fees(slug)
        revenue_raw = fetch_protocol_revenue(slug)
        volume_raw = fetch_protocol_volume(slug)

        for chain in CHAINS_OF_INTEREST:
            df = base_df.copy()
            tvl_df = tvl_to_df(tvl_raw, chain)
            if not tvl_df.empty:
                df = df.merge(tvl_df, on="date", how="left")
            else:
                df['tvl'] = np.nan
            
            fees_df = fees_to_df(fees_raw, chain) if fees_raw else pd.DataFrame()
            if not fees_df.empty:
                df = df.merge(fees_df, on="date", how="left")
            else:
                df['fees'] = np.nan
            
            revenue_df = revenue_to_df(revenue_raw, chain) if revenue_raw else pd.DataFrame()
            if not revenue_df.empty:
                df = df.merge(revenue_df, on="date", how="left")
            else:
                df['revenue'] = np.nan
                
            volume_df = volume_to_df(revenue_raw, chain) if volume_raw else pd.DataFrame()
            if not volume_df.empty:
                df = df.merge(volume_df, on="date", how="left")
            else:
                df['volume'] = np.nan

            # Fill missing values
            df[["tvl","fees","revenue","volume"]] = df[["tvl","fees","revenue","volume"]].ffill()

            # Add identifiers
            df["protocol"] = protocol_name
            df["chain"] = chain
            df["expenses"] = df["fees"] - df["revenue"]  # optional placeholder

            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()



# Get metrics for the cards
def get_current_metrics():
    protocol_df = generate_protocol_data()
    latest_date = protocol_df['date'].max()

    latest_data = protocol_df[protocol_df['date'] == latest_date]

    return {
        'total_tvl': latest_data['tvl'].sum(),
        'total_fees': latest_data['fees'].sum(),
        'total_revenue': latest_data['revenue'].sum(),
        'total_volume': latest_data['volume'].sum(),
        'active_chains': len(latest_data['chain']),
        'active_protocols': len(latest_data['protocol'].unique())
    } 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# Pool-Level Data (Type 2)
def generate_pool_data():
    pools = [
        {'protocol': 'Uniswap', 'name': 'ETH-USDC', 'version': 'v3'},
        {'protocol': 'Uniswap', 'name': 'ETH-USDT', 'version': 'v3'},
        {'protocol': 'Uniswap', 'name': 'BTC-ETH', 'version': 'v3'},
        {'protocol': 'Uniswap', 'name': 'ETH-DAI', 'version': 'v2'},
        {'protocol': 'Aave', 'name': 'ETH Supply', 'version': 'v3'},
        {'protocol': 'Aave', 'name': 'USDC Supply', 'version': 'v3'},
        {'protocol': 'Aave', 'name': 'DAI Borrow', 'version': 'v2'},
        {'protocol': 'Compound', 'name': 'ETH Supply', 'version': 'v3'},
        {'protocol': 'Compound', 'name': 'USDC Borrow', 'version': 'v3'},
        {'protocol': 'Curve', 'name': '3pool', 'version': 'v2'},
        {'protocol': 'Curve', 'name': 'stETH-ETH', 'version': 'v2'},
        {'protocol': 'dYdX', 'name': 'ETH-USD', 'version': 'v4'},
    ]
    
    chains = ['Ethereum', 'Polygon', 'Arbitrum', 'Optimism', 'Base']
    date_range = generate_date_range()
    
    data = []
    
    for pool in pools:
        # Base values differ by pool
        base_tvl = np.random.uniform(10000000, 500000000)
        base_fees = np.random.uniform(5000, 100000)
        base_volume = np.random.uniform(1000000, 50000000)
        base_utilization = np.random.uniform(0.3, 0.7) if 'Supply' in pool['name'] or 'Borrow' in pool['name'] else None
        base_supply_rate = np.random.uniform(0.01, 0.1) if 'Supply' in pool['name'] else None
        base_borrow_rate = np.random.uniform(0.03, 0.15) if 'Borrow' in pool['name'] else None
        
        for date in date_range:
            # Add time-based trends
            day_factor = 1 + 0.001 * (date_range.get_loc(date) - len(date_range)/2)
            day_factor *= np.random.uniform(0.93, 1.07)  # More volatility at pool level
            
            # Only include certain chains based on the protocol
            valid_chains = chains if pool['protocol'] != 'dYdX' else ['Ethereum', 'Base']
            
            for chain in valid_chains:
                # Some pools only exist on certain chains
                if np.random.random() > 0.6:  # 40% chance to skip this chain for this pool
                    continue
                    
                # Data for this day and chain
                tvl = base_tvl * day_factor * np.random.uniform(0.8, 1.2)
                fees = base_fees * day_factor * np.random.uniform(0.7, 1.3)
                volume = base_volume * day_factor * np.random.uniform(0.5, 1.5)
                
                pool_data = {
                    'date': date,
                    'protocol': pool['protocol'],
                    'pool_name': pool['name'],
                    'version': pool['version'],
                    'chain': chain,
                    'tvl': tvl,
                    'fees': fees,
                    'volume': volume,
                }
                
                # Add lending-specific metrics for lending protocols
                if pool['protocol'] in ['Aave', 'Compound']:
                    utilization = base_utilization * day_factor * np.random.uniform(0.9, 1.1)
                    utilization = min(max(utilization, 0.1), 0.95)  # Keep between 10% and 95%
                    
                    pool_data['utilization_rate'] = utilization
                    
                    if 'Supply' in pool['name']:
                        pool_data['supply_rate'] = base_supply_rate * day_factor * np.random.uniform(0.9, 1.1)
                    
                    if 'Borrow' in pool['name']:
                        pool_data['borrow_rate'] = base_borrow_rate * day_factor * np.random.uniform(0.9, 1.1)
                
                data.append(pool_data)
    
    return pd.DataFrame(data)

# Transaction-Level Data
def generate_transaction_data(n_transactions=100):
    protocols = ['Uniswap', 'Aave', 'Compound', 'Curve', 'dYdX']
    chains = ['Ethereum', 'Polygon', 'Arbitrum', 'Optimism', 'Base']
    action_types = ['Swap', 'Supply', 'Borrow', 'Repay', 'Withdraw']
    
    data = []
    
    for i in range(n_transactions):
        protocol = np.random.choice(protocols)
        
        # Determine action type based on protocol
        if protocol in ['Uniswap', 'Curve']:
            action = 'Swap'
        elif protocol in ['Aave', 'Compound']:
            action = np.random.choice(['Supply', 'Borrow', 'Repay', 'Withdraw'])
        else:
            action = np.random.choice(action_types)
            
        # Random transaction time in last 7 days
        tx_time = datetime.now() - timedelta(days=np.random.uniform(0, 7))
        
        # Generate random wallet address
        wallet = '0x' + ''.join(np.random.choice(list('0123456789abcdef'), 40))
        
        # Generate amount based on action type
        if action == 'Swap':
            amount = np.random.uniform(100, 50000)
        elif action in ['Supply', 'Borrow']:
            amount = np.random.uniform(1000, 100000)
        else:
            amount = np.random.uniform(500, 20000)
            
        # Generate gas fee
        gas_fee = np.random.uniform(5, 100)
        
        data.append({
            'timestamp': tx_time,
            'protocol': protocol,
            'chain': np.random.choice(chains),
            'wallet_address': wallet,
            'action': action,
            'amount_usd': amount,
            'gas_fee_usd': gas_fee,
            'transaction_hash': '0x' + ''.join(np.random.choice(list('0123456789abcdef'), 64))
        })
    
    return pd.DataFrame(data)

