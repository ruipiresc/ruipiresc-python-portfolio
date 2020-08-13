from functools import lru_cache
import pyEX as iex

client = iex.Client()

@lru_cache
def _get_quote(symbol:str) -> dict:
    if symbol == 'VUSA':
        quote = client.quote('V')
        for key in quote.keys():
            quote[key] = 'None'
        return quote
    return client.quote(symbol)

@lru_cache
def _get_company(symbol:str) -> dict:
    if symbol == 'VUSA':
        company = client.company('V')
        for key in company.keys():
            company[key] = 'None'
        return company
    return client.company(symbol)

def get_company_details(symbol: str) -> dict:
    return _get_company(symbol)

def get_price(symbol: str) -> float:
    return _get_quote(symbol)['latestPrice']
