#!/usr/bin/env python3
# Script pour visualiser tous les relevés de marchés, news et analyses techniques

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.market_notes import get_market_notes, print_market_notes
from app.utils.news_tracker import get_news_tracker, print_news_report
from app.utils.technical_analyzer import get_technical_analyzer, print_analysis_report
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone, timedelta

def view_all_reports():
    """Affiche tous les relevés disponibles"""
    print("=" * 70)
    print("📊 SYSTÈME DE RELEVÉS DE MARCHÉS - ADAM")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Relevés de notes de marché
    print("=" * 70)
    print("📝 1. NOTES DE MARCHÉ")
    print("=" * 70)
    
    notes = get_market_notes()
    if notes.notes:
        print(f"✅ {len(notes.notes)} marchés avec des notes")
        print("\nMarchés disponibles:")
        for symbol in notes.notes.keys():
            summary = notes.get_market_summary(symbol)
            print(f"  • {symbol}: {summary['total_notes']} notes (Dernière: {summary['last_updated']})")
        
        # Afficher les notes de quelques marchés
        print("\n📋 Détail des notes par marché:")
        for symbol in list(notes.notes.keys())[:5]:  # Top 5
            print_market_notes(symbol)
    else:
        print("ℹ️ Aucune note de marché enregistrée")
    
    # 2. Relevés de news
    print("\n" + "=" * 70)
    print("📰 2. RELEVÉS DE NEWS")
    print("=" * 70)
    
    tracker = get_news_tracker()
    if tracker.news_data:
        summary = tracker.get_news_summary()
        print(f"✅ {summary['total_news']} news enregistrées")
        print(f"   Période: {summary['period']}")
        print(f"   News à fort impact: {summary['high_impact_news']}")
        
        if summary['news_by_symbol']:
            print("\nNews par symbole:")
            for sym, count in sorted(summary['news_by_symbol'].items(), key=lambda x: x[1], reverse=True):
                print(f"  • {sym}: {count} news")
        
        # Afficher le rapport détaillé
        print("\n📋 Détail des news récentes:")
        print_news_report()
    else:
        print("ℹ️ Aucune news enregistrée")
    
    # 3. Analyses techniques
    print("\n" + "=" * 70)
    print("📈 3. ANALYSES TECHNIQUES")
    print("=" * 70)
    
    analyzer = get_technical_analyzer()
    if analyzer.analysis_data:
        print(f"✅ {len(analyzer.analysis_data)} paires timeframes analysées")
        print("\nAnalyses disponibles:")
        
        for key in analyzer.analysis_data.keys():
            symbol, timeframe = key.split('_')
            summary = analyzer.get_analysis_summary(symbol, timeframe)
            if 'error' not in summary:
                print(f"  • {symbol} ({timeframe}): Score moyen {summary['avg_quality_score']}/100")
        
        # Afficher les rapports détaillés
        print("\n📋 Rapports détaillés par marché:")
        for key in list(analyzer.analysis_data.keys())[:3]:  # Top 3
            symbol, timeframe = key.split('_')
            print_analysis_report(symbol, timeframe)
    else:
        print("ℹ️ Aucune analyse technique enregistrée")
        print("💡 Pour générer des analyses, connectez-vous à MT5 et utilisez:")
        print("   python -c \"from app.utils.technical_analyzer import analyze_market_structure\"")
    
    print("\n" + "=" * 70)
    print("📁 FICHIERS DE DONNÉES")
    print("=" * 70)
    print("Les données sont sauvegardées dans les fichiers suivants:")
    print("  • market_notes.json    - Notes de marché")
    print("  • news_tracker.json    - Suivi des news")
    print("  • technical_analysis.json - Analyses techniques")
    print()
    
    # Vérifier si les fichiers existent
    files = {
        "market_notes.json": "Notes de marché",
        "news_tracker.json": "Suivi des news", 
        "technical_analysis.json": "Analyses techniques"
    }
    
    for filename, description in files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✅ {filename} ({description}): {size} octets")
        else:
            print(f"  ❌ {filename} ({description}): Non créé")
    
    print("\n" + "=" * 70)
    print("💡 UTILISATION")
    print("=" * 70)
    print("Pour ajouter des données:")
    print("  • Notes: from app.utils.market_notes import add_technical_observation")
    print("  • News: from app.utils.news_tracker import add_news_event")
    print("  • Analyse: from app.utils.technical_analyzer import analyze_market_structure")
    print()
    print("Pour afficher les rapports:")
    print("  • python view_reports.py")
    print("=" * 70)


def generate_real_analysis():
    """Génère des analyses techniques réelles depuis MT5"""
    print("📈 GÉNÉRATION D'ANALYSES TECHNIQUES RÉELLES")
    print("=" * 70)
    
    # Connexion à MT5
    if not mt5.initialize():
        print("❌ Impossible de se connecter à MT5")
        return
    
    print("✅ MT5 connecté")
    
    # Symboles à analyser
    symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    timeframe = "M5"
    
    from app.utils.technical_analyzer import analyze_market_structure
    
    for symbol in symbols:
        print(f"\n📊 Analyse de {symbol}...")
        
        # Récupérer les données
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
        
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Analyser
            analysis = analyze_market_structure(symbol, df, timeframe)
            
            if 'error' not in analysis:
                print(f"✅ {symbol} analysé: Score {analysis['quality_score']}/100")
            else:
                print(f"❌ Erreur analyse {symbol}: {analysis['error']}")
        else:
            print(f"❌ Impossible de récupérer les données pour {symbol}")
    
    mt5.shutdown()
    print("\n✅ Analyses techniques générées avec succès!")
    print("Lancez 'python view_reports.py' pour voir les relevés.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualiser les relevés de marchés')
    parser.add_argument('--analyze', action='store_true', help='Générer des analyses techniques réelles depuis MT5')
    
    args = parser.parse_args()
    
    if args.analyze:
        generate_real_analysis()
    else:
        view_all_reports()
