import datetime as dt
from dataclasses import dataclass, field
import pandas as pd
from .utils import to_df, to_dict

@dataclass
class Holding:
    """Class for keeping track of an holding."""
    symbol: str
    currency: str
    exchange: str
    quantity: float
    exchange_rate: float
    price_native: float
    price: float = field(default = 0.0)
    market_value: float = field(default = 0.0)
    market_value_native: float = field(default = 0.0)
    timestamp: dt.datetime = field(default = dt.datetime.now())
    id: str = field(default = '')

    def __post_init__(self):
        self.id = ':'.join([self.exchange, self.symbol, self.currency])
        self.price = self.exchange_rate * self.price_native
        self.market_value = self.quantity * self.price
        self.market_value_native = self.quantity * self.price_native

    def to_dict(self) -> dict:
        return to_dict(self)

    def to_df(self) -> pd.DataFrame:
        return to_df(self)