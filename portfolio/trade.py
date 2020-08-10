import datetime as dt
from dataclasses import dataclass, field
from .utils import to_dict

@dataclass
class Trade:
    """Class for keeping track of a trade."""
    position_id: str
    symbol: str
    isin: str
    quantity: float
    direction: str
    price: float
    comission: float
    tax: float
    order_type: str
    execution_venue: str
    exchange_rate: float
    timestamp: dt.datetime
    statement_id: str
    total_amount: float = field(default = 0.0)
    total_amount_native: float = field(default = 0.0)
    total_cost: float = field(default = 0.0)
    id: str = field(default = '')

    def __post_init__(self):
        self.id = '_'.join([self.statement_id, self.timestamp.isoformat(), self.symbol, self.direction, str(self.quantity)])
        if self.direction.lower() == 'sell' and self.quantity > 0:
            self.quantity = -self.quantity
        self.total_amount = self.price * self.quantity
        self.total_amount_native = self.total_amount * self.exchange_rate
        self.total_cost = self.total_amount + self.comission + self.tax

    def to_dict(self) -> dict:
        return to_dict(self)