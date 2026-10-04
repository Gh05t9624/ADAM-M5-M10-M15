# Script pour vérifier les trades MT5 d'hier
import sys
sys.path.insert(0, '.')

from app.data.mt5_provider import MT5Provider
from datetime import datetime, timedelta
import MetaTrader5 as mt5

def check_yesterday_trades():
    """Vérifie les trades d'hier sur le compte MT5"""
    print("🔍 Connexion à MT5...")
    
    try:
        provider = MT5Provider()
        print("✅ Connecté à MT5")
        
        # Récupérer les infos du compte
        account = provider.get_account_info()
        if account:
            print(f"\n📊 Info Compte:")
            print(f"  - Nom: {account.name}")
            print(f"  - Balance: {account.balance}")
            print(f"  - Equity: {account.equity}")
            print(f"  - Marge: {account.margin}")
        else:
            print("⚠️ Impossible de récupérer les infos du compte")
        
        # Récupérer les trades depuis samedi (entrée samedi, fermé hier)
        print(f"\n🔍 Récupération des trades depuis samedi...")
        
        # Calculer la date de début (samedi)
        days_ago = datetime.now().weekday()  # 0=Lundi, 6=Dimanche
        if days_ago == 0:  # Lundi
            from_date = datetime.now() - timedelta(days=3)  # Samedi
        elif days_ago == 1:  # Mardi
            from_date = datetime.now() - timedelta(days=4)  # Samedi
        else:
            from_date = datetime.now() - timedelta(days=days_ago + 1)  # Samedi
        
        to_date = datetime.now()
        
        print(f"  - Du: {from_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - Au: {to_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📡 Appel à mt5.history_deals_get...")
        # Récupérer les deals (trades)
        deals = mt5.history_deals_get(from_date, to_date)
        print(f"✅ Deals récupérés: {len(deals) if deals else 0}")
        
        if deals is None or len(deals) == 0:
            print("❌ Aucun trade trouvé dans cette période")
            return
        
        # Convertir en DataFrame
        import pandas as pd
        df = pd.DataFrame(list(deals))
        
        # Filtrer pour ne garder que les trades fermés (profit != 0)
        if 'profit' in df.columns:
            df = df[df['profit'] != 0]
        else:
            print("⚠️ Aucune colonne 'profit' trouvée")
            return
        
        print(f"\n📋 {len(df)} trades trouvés:\n")
        
        # Afficher les trades
        for idx, trade in df.iterrows():
            trade_time = datetime.fromtimestamp(trade['time']).strftime('%Y-%m-%d %H:%M:%S')
            profit = trade['profit']
            symbol = trade['symbol']
            volume = trade['volume']
            deal_type = 'ACHAT' if trade['type'] == 0 else 'VENTE' if trade['type'] == 1 else 'INCONNU'
            
            profit_emoji = "📉" if profit < 0 else "📈"
            
            print(f"{profit_emoji} {symbol} | {deal_type} | Volume: {volume} | Profit: {profit:.2f} | {trade_time}")
        
        # Filtrer les trades perdants
        losing_trades = df[df['profit'] < 0]
        print(f"\n❌ Trades perdants: {len(losing_trades)}")
        
        if len(losing_trades) > 0:
            print("\nDétails des trades perdants:")
            for idx, trade in losing_trades.iterrows():
                trade_time = datetime.fromtimestamp(trade['time']).strftime('%Y-%m-%d %H:%M:%S')
                profit = trade['profit']
                symbol = trade['symbol']
                volume = trade['volume']
                price = trade['price']
                deal_type = 'ACHAT' if trade['type'] == 0 else 'VENTE' if trade['type'] == 1 else 'INCONNU'
                
                print(f"  - {symbol} | {deal_type} | Prix: {price} | Volume: {volume} | Perte: {profit:.2f} | {trade_time}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    check_yesterday_trades()
