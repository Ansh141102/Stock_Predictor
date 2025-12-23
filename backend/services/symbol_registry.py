"""
Symbol Registry Service
Manages NSE/BSE stock symbols with fuzzy search capabilities
"""
import json
import os
from typing import List, Dict, Optional
from difflib import get_close_matches

class SymbolRegistry:
    def __init__(self, symbols_file: str = "data/symbols.json"):
        self.symbols_file = symbols_file
        self.symbols: List[Dict] = []
        self.symbol_map: Dict[str, Dict] = {}
        self._load_symbols()
    
    def _load_symbols(self):
        """Load symbols from JSON file or create default list"""
        if os.path.exists(self.symbols_file):
            with open(self.symbols_file, 'r', encoding='utf-8') as f:
                self.symbols = json.load(f)
        else:
            # Default NSE/BSE symbols - Top companies
            self.symbols = self._get_default_symbols()
            self._save_symbols()
        
        # Create lookup map
        for symbol in self.symbols:
            self.symbol_map[symbol['symbol']] = symbol
            self.symbol_map[symbol['name'].upper()] = symbol
    
    def _get_default_symbols(self) -> List[Dict]:
        """Return default list of major NSE/BSE stocks"""
        return [
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "exchange": "NSE"},
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "exchange": "NSE"},
            {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "exchange": "NSE"},
            {"symbol": "INFY.NS", "name": "Infosys", "exchange": "NSE"},
            {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "exchange": "NSE"},
            {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "exchange": "NSE"},
            {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE"},
            {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
            {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "exchange": "NSE"},
            {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "exchange": "NSE"},
            {"symbol": "LT.NS", "name": "Larsen & Toubro", "exchange": "NSE"},
            {"symbol": "AXISBANK.NS", "name": "Axis Bank", "exchange": "NSE"},
            {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "exchange": "NSE"},
            {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "exchange": "NSE"},
            {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical", "exchange": "NSE"},
            {"symbol": "TITAN.NS", "name": "Titan Company", "exchange": "NSE"},
            {"symbol": "WIPRO.NS", "name": "Wipro", "exchange": "NSE"},
            {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "exchange": "NSE"},
            {"symbol": "NESTLEIND.NS", "name": "Nestle India", "exchange": "NSE"},
            {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "exchange": "NSE"},
            {"symbol": "TECHM.NS", "name": "Tech Mahindra", "exchange": "NSE"},
            {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "exchange": "NSE"},
            {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation", "exchange": "NSE"},
            {"symbol": "NTPC.NS", "name": "NTPC Limited", "exchange": "NSE"},
            {"symbol": "ONGC.NS", "name": "Oil and Natural Gas Corporation", "exchange": "NSE"},
            {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "exchange": "NSE"},
            {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "exchange": "NSE"},
            {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "exchange": "NSE"},
            {"symbol": "ADANIPORTS.NS", "name": "Adani Ports", "exchange": "NSE"},
            {"symbol": "COALINDIA.NS", "name": "Coal India", "exchange": "NSE"},
            {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "exchange": "NSE"},
            {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "exchange": "NSE"},
            {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories", "exchange": "NSE"},
            {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "exchange": "NSE"},
            {"symbol": "GRASIM.NS", "name": "Grasim Industries", "exchange": "NSE"},
            {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "exchange": "NSE"},
            {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "exchange": "NSE"},
            {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "exchange": "NSE"},
            {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "exchange": "NSE"},
            {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "exchange": "NSE"},
            {"symbol": "CIPLA.NS", "name": "Cipla", "exchange": "NSE"},
            {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "exchange": "NSE"},
            {"symbol": "BPCL.NS", "name": "Bharat Petroleum", "exchange": "NSE"},
            {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "exchange": "NSE"},
            {"symbol": "SHREECEM.NS", "name": "Shree Cement", "exchange": "NSE"},
            {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "exchange": "NSE"},
            {"symbol": "UPL.NS", "name": "UPL Limited", "exchange": "NSE"},
            {"symbol": "VEDL.NS", "name": "Vedanta Limited", "exchange": "NSE"},
            {"symbol": "GODREJCP.NS", "name": "Godrej Consumer Products", "exchange": "NSE"},
            {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "exchange": "NSE"},
        ]
    
    def _save_symbols(self):
        """Save symbols to JSON file"""
        os.makedirs(os.path.dirname(self.symbols_file), exist_ok=True)
        with open(self.symbols_file, 'w', encoding='utf-8') as f:
            json.dump(self.symbols, f, indent=2, ensure_ascii=False)
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Fuzzy search for stock symbols
        
        Args:
            query: Search query (company name or symbol)
            limit: Maximum number of results
            
        Returns:
            List of matching stock dictionaries
        """
        if not query:
            return self.symbols[:limit]
        
        query = query.upper().strip()
        
        # Exact match first
        if query in self.symbol_map:
            return [self.symbol_map[query]]
        
        # Fuzzy match on names and symbols
        all_keys = list(self.symbol_map.keys())
        matches = get_close_matches(query, all_keys, n=limit, cutoff=0.4)
        
        results = []
        seen = set()
        for match in matches:
            symbol_data = self.symbol_map[match]
            if symbol_data['symbol'] not in seen:
                results.append(symbol_data)
                seen.add(symbol_data['symbol'])
        
        return results[:limit]
    
    def get_symbol(self, symbol: str) -> Optional[Dict]:
        """Get stock data by exact symbol"""
        return self.symbol_map.get(symbol.upper())
    
    def add_symbol(self, symbol: str, name: str, exchange: str = "NSE"):
        """Add a new symbol to the registry"""
        symbol_data = {
            "symbol": symbol.upper(),
            "name": name,
            "exchange": exchange
        }
        self.symbols.append(symbol_data)
        self.symbol_map[symbol_data['symbol']] = symbol_data
        self.symbol_map[symbol_data['name'].upper()] = symbol_data
        self._save_symbols()
    
    def get_all_symbols(self) -> List[Dict]:
        """Return all symbols"""
        return self.symbols


# Singleton instance
_registry = None

def get_registry() -> SymbolRegistry:
    """Get or create symbol registry instance"""
    global _registry
    if _registry is None:
        _registry = SymbolRegistry()
    return _registry
