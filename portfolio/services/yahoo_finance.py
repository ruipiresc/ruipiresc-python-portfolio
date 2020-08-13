from functools import lru_cache
import yfinance as yf

@lru_cache
def _get_ticker(name:str) -> yf.Ticker:
    if name == 'VUSA': name = 'VUSA.L'
    return yf.Ticker(name)

def get_last_price(symbol: str) -> float:
    return _get_ticker(symbol).info['regularMarketPrice']

def get_exchange_rate(from_currency: str,to_currency: str) -> float:
    return _get_ticker(to_currency + from_currency + '=X').info['regularMarketPrice']

def get_fundamentals(symbol: str) -> dict:
    return _get_ticker(symbol).info
