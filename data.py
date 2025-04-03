import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate date range for time series data
def generate_date_range(days=180):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return pd.date_range(start=start_date, end=end_date, freq='D')

# Protocol-Level Data (Type 1)
def generate_protocol_data():
    protocols = ['Uniswap', 'Aave', 'Compound', 'Curve', 'dYdX']
    chains = ['Ethereum', 'Polygon', 'Arbitrum', 'Optimism', 'Base']
    date_range = generate_date_range()
    
    data = []
    
    for protocol in protocols:
        # Base values differ by protocol
        base_tvl = np.random.uniform(500000000, 2000000000)
        base_fees = np.random.uniform(50000, 500000)
        base_revenue = base_fees * np.random.uniform(0.1, 0.5)
        base_expenses = base_revenue * np.random.uniform(0.2, 0.8)
        base_volume = np.random.uniform(10000000, 100000000)
        
        # Time series with trends and some volatility
        for date in date_range:
            # Add time-based trends (generally upward with some volatility)
            day_factor = 1 + 0.001 * (date_range.get_loc(date) - len(date_range)/2) 
            day_factor *= np.random.uniform(0.95, 1.05)  # Add some randomness
            
            # Data for this day
            tvl = base_tvl * day_factor
            fees = base_fees * day_factor
            revenue = fees * np.random.uniform(0.1, 0.5)
            expenses = revenue * np.random.uniform(0.2, 0.8)
            volume = base_volume * day_factor
            
            # Split across chains
            for chain in chains:
                chain_factor = np.random.uniform(0.05, 0.5)  # Different distribution per chain
                
                data.append({
                    'date': date,
                    'protocol': protocol,
                    'chain': chain,
                    'tvl': tvl * chain_factor,
                    'fees': fees * chain_factor,
                    'revenue': revenue * chain_factor,
                    'expenses': expenses * chain_factor,
                    'volume': volume * chain_factor
                })
    
    return pd.DataFrame(data)

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
        'active_chains': len(latest_data['chain'].unique()),
        'active_protocols': len(latest_data['protocol'].unique())
    } 