import datetime as dt
from dataclasses import dataclass, field
import pandas as pd
from .utils import to_df, to_dict

@dataclass
class Statement:
    """Class for keeping track of an item in inventory."""
    date: dt.date
    email_id: str
    broker_id: str
    id: str = field(default='')

    def __post_init__(self):
        self.id = '_'.join([str(self.date), self.broker_id, self.email_id])

    def to_dict(self) -> dict:
        return to_dict(self)
    
    def to_df(self) -> pd.DataFrame:
        return to_df(self)
