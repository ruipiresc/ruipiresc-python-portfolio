import datetime as dt
from typing import Any
import wraplite as wl
import pandas as pd
from .holding import Holding
from .services import alpha_vantage, iex_cloud, yahoo_finance
from . import gmail, trading212, utils

class Portfolio(object):
  """Your portfolio class."""

  database_name: str = 'portfolio'
  base_currency: str = 'EUR'
  _db: wl.Database = None
  _gmail: Any = None

  def __init__(self) -> None:
    self.gmail

  def setup(self) -> str:
    self.db.create_table('brokers', wl.table.TableFormat(
      id= str,
      name= str,
      account= str,
      account_type= str,
      currency= str
    ).primary_keys(['id']))

    self.db.create_table('statements', wl.table.TableFormat(
      id= str,
      date= dt.date,
      email_id= str,
      broker_id= str
    ).primary_keys(['id']))

    self.db.create_table('trades', wl.table.TableFormat(
      id= str,
      position_id= str,
      symbol= str,
      isin= str,
      quantity= float,
      direction= str,
      price= float,
      comission= float,
      tax= float,
      total_amount= float,
      total_amount_native= float,
      total_cost= float,
      order_type= str,
      execution_venue= str,
      exchange_rate= float,
      timestamp= dt.datetime,
      statement_id= str
    ).primary_keys(['id']))
  
    self.db.create_table('holdings', wl.table.TableFormat(
      id= str,
      symbol= str,
      exchange= str,
      currency= str,
      quantity= float,
      price= float,
      market_value= float,
      price_native= float,
      market_value_native= float,
      exchange_rate= float,
      timestamp= dt.datetime
    ).primary_keys(['id', 'timestamp']))

    self.data.setup()
    return 'setup completed'

  @property
  def db(self) -> wl.Database:
    if self._db == None:
      self._db = wl.get(self.database_name)
    return self._db

  @property
  def gmail(self) -> Any:
    if self._gmail == None:
      self._gmail = gmail.get_service()
    return self._gmail

  def update(self) -> str:
    def update_trades() -> None:
      email_ids = gmail.search_messages(service = self.gmail, user_id = 'me', query = trading212.build_gmail_query())
      for email_id in email_ids:
        if len(self.db.statements.query(f"SELECT * FROM statements WHERE email_id='{email_id}'")) == 0:
          email = gmail.get_message(service = self.gmail, user_id = 'me', msg_id = email_id)
          broker, statement, trades = trading212.process_email_statement(email, email_id)
          if len(self.db.brokers.query(f"SELECT * FROM brokers WHERE id='{broker.id}'")) == 0:
            self.db.brokers.insert(utils.to_df(broker))
            print(f'added broker: {broker.name}')
          self.db.statements.insert(utils.to_df(statement))
          money_invested = sum(trade.total_cost for trade in trades)
          print(f'processed statement from "{broker.name}" of <{statement.date}> with #{len(trades)} trades and {money_invested} {broker.currency} invested')
          self.db.trades.insert(utils.to_df(trades))
    def update_holdings() -> None:
      trades: pd.DataFrame = self.db.trades.get_all()
      holdings = []
      for symbol in trades.symbol.unique():
        symbol_trades = trades[trades['symbol']==symbol]
        stock_fundamentals = yahoo_finance.get_fundamentals(symbol)
        holdings.append(Holding(
          symbol= symbol,
          currency= stock_fundamentals['currency'],
          exchange= stock_fundamentals['exchange'],
          quantity= symbol_trades.quantity.sum(),
          exchange_rate= yahoo_finance.get_exchange_rate(stock_fundamentals['currency'], self.base_currency),
          price_native= yahoo_finance.get_last_price(symbol),
        ))
      self.db.holdings.insert(utils.to_df(holdings))
    update_trades()
    update_holdings()
    return 'portfolio trades and tickers updated'

  def money_invested(self) -> str:
    results = []
    brokers: pd.Dataframe = self.db.brokers.get_all()
    for _, broker in brokers.iterrows():
      money_invested = 0.0
      statements = self.db.statements.query(f"SELECT * FROM statements WHERE broker_id='{broker.id}'")
      for _, statement in statements.iterrows():
        trades = self.db.trades.query(f"SELECT * FROM trades WHERE statement_id='{statement.id}'")
        money_invested += trades.total_cost.sum()
      results.append('you have {} {} invested on {}'.format(money_invested, broker.currency, broker['name']))
    return results
  
  def print(self, table_name: str) -> str:
    if hasattr(self.db, table_name):
      return str(getattr(self.db, table_name))
    if hasattr(self.data.db, table_name):
      return str(getattr(self.data.db, table_name))
    return 'nothing to print'
  
  def drop(self, table_name: str) -> str:
    result = []
    if hasattr(self.db, table_name):
      getattr(self.db, table_name).drop()
      result.append(f'dropped table {table_name} from portfolio db')
    if hasattr(self.data.db, table_name):
      getattr(self.data.db, table_name).drop()
      result.append(f'dropped table {table_name} from iex db')
    return result

  def dump(self, table_name: str) -> str:
    table: wl.Table = getattr(self.db, table_name)
    rows: pd.DataFrame = table.get_all()
    rows.to_excel(table_name + '.xlsx')
    return f'dumped table: {table_name}'
