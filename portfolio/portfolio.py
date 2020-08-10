import datetime as dt
from typing import Any
import wraplite as wl
import pandas as pd
from . import gmail, trading212, utils

class Portfolio(object):
  """Your portfolio class."""

  database_name: str = 'portfolio'
  _db = None
  _gmail = None

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

  def set_up(self) -> str:
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

    self.gmail
    return 'tables and connection to gmail ok. Set up complete'

  def update(self) -> str:
    def update_trades() -> None:
      email_ids = gmail.search_messages(service = self.gmail, user_id = 'me', query = trading212.build_gmail_query())
      for email_id in email_ids:
        if len(self.db.statements.query(f'SELECT * FROM statements WHERE email_id=\'{email_id}\'')) == 0:
          email = gmail.get_message(service = self.gmail, user_id = 'me', msg_id = email_id)
          broker, statement, trades = trading212.process_email_statement(email, email_id)
          if len(self.db.brokers.query(f'SELECT * FROM brokers WHERE id=\'{broker.id}\'')) == 0:
            self.db.brokers.insert(utils.to_df(broker))
            print(f'added broker: {broker.name}')
          self.db.statements.insert(utils.to_df(statement))
          money_invested = sum(trade.total_cost for trade in trades)
          print(f'processed statement from "{broker.name}" of <{statement.date}> with #{len(trades)} trades and {money_invested} {broker.currency} invested')
          self.db.trades.insert(utils.to_df(trades))
    update_trades()
    return 'portfolio trades and tickers updated'

  def trades(self) -> str:
    return str(self.db.trades.get_all())
  
  def statements(self) -> str:
    return str(self.db.statements.get_all())

  def brokers(self) -> str:
    return str(self.db.brokers.get_all())

  def money_invested(self) -> str:
    results = []
    brokers: pd.Dataframe = self.db.brokers.get_all()
    for _, broker in brokers.iterrows():
      money_invested = 0.0
      statements = self.db.statements.query(f'SELECT * FROM statements WHERE broker_id=\'{broker.id}\'')
      for _, statement in statements.iterrows():
        trades = self.db.trades.query(f'SELECT * FROM trades WHERE statement_id=\'{statement.id}\'')
        money_invested += trades.total_cost.sum()
      results.append('you have {} {} invested on {}'.format(money_invested, broker.currency, broker['name']))
    return results

  def dump(self, table_name: str) -> str:
    table: wl.Table = getattr(self.db, table_name)
    rows: pd.DataFrame = table.get_all()
    rows.to_excel(table_name + '.xlsx')
    return f'dumped table: {table_name}'
