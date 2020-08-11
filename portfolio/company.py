import datetime as dt
from dataclasses import dataclass, field
import pandas as pd
from .utils import to_df, to_dict

@dataclass
class Company:
    """Class for keeping track of a Company."""
    symbol: str
    currency: str
    company_name: str
    exchange: str
    industry: str
    website: str
    description: str
    country: str
    ceo: str
    security_name: str
    issue_type: str
    sector: str
    tags: str
    date_added: dt.date
    id: str = field(default = '')

    def __post_init__(self):
        self.id = ':'.join([self.exchange, self.symbol, self.currency])

    def to_dict(self) -> dict:
        return to_dict(self)

    def to_df(self) -> pd.DataFrame:
        return to_df(self)