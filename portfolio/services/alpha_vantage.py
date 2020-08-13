from functools import lru_cache
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.foreignexchange import ForeignExchange

ts = TimeSeries(output_format='json')
sp = SectorPerformances(output_format='pandas')
fe = ForeignExchange(output_format='json')
cc = CryptoCurrencies(output_format='pandas')

@lru_cache
def _get_quote(name:str) -> dict:
    return ts.get_quote_endpoint(name)[0]

@lru_cache
def _get_currency_exchange_rate(from_currency: str,to_currency: str) -> dict:
    return fe.get_currency_exchange_rate(from_currency, to_currency)[0]

def get_last_price(symbol:str) -> float:
   return float(_get_quote(symbol)['05. price'])

def get_exchange_rate(from_currency: str,to_currency: str) -> float:
    return float(_get_currency_exchange_rate(from_currency, to_currency)['5. Exchange Rate'])
