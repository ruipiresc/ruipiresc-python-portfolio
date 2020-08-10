import email
import datetime as dt
from typing import List, Tuple
from .broker import Broker
from .trade import Trade
from .statement import Statement

def build_gmail_query() -> str:
    sender ='noreply@trading212.com'
    subject_starts_with = 'Contract Note'
    return 'from:{} subject:{}*'.format(sender, subject_starts_with)

def process_email_statement(msg: email.message.EmailMessage, msg_id: str) -> Tuple[Broker, Statement, List[Trade]]:
    def process_email_body(body: str) -> List[str]:
        body = body.replace('&nbsp;',' ')
        while '\n ' in body: body = body.replace('\n ', '\n')
        while '\n\n' in body: body = body.replace('\n\n', '\n')
        while '  ' in body: body = body.replace('  ', ' ')
        return body.split('\n')

    body_lines = process_email_body(str(msg._payload[0]))
    date: str = body_lines[11].replace('We confirm the following transactions for: ','')

    broker = Broker('trading212', body_lines[6], body_lines[8], body_lines[10])
    statement = Statement(
        date = dt.date(int(date[0:4]),int(date[5:7]), int(date[8:10])),
        email_id = msg_id,
        broker_id = broker.id
    )

    def get_trades(lines: List[str]) -> List[Trade]:
        index = 0
        while lines[index] != '№':
            index += 1
        lines[index] = 'N'
        trade_keys = []
        while lines[index] != '1':
            trade_keys.append(lines[index])
            index += 1
        def get_trade(raw_trade: dict) -> Trade:
            day = int(raw_trade['Trading day'][0:2])
            month = int(raw_trade['Trading day'][3:5])
            year = int(raw_trade['Trading day'][6:10])
            hours = int(raw_trade['Trading time'][0:2])
            minutes = int(raw_trade['Trading time'][3:5])
            seconds = int(raw_trade['Trading time'][6:8])
            date = dt.date(year, month, day)
            time = dt.time(hours, minutes, seconds)
            return Trade(
                position_id = raw_trade['Order ID'].strip(),
                symbol = raw_trade['Instrument/ISIN'].split('/')[0].strip(),
                isin = raw_trade['Instrument/ISIN'].split('/')[1].strip(),
                quantity = float(raw_trade['Quantity']),
                direction = raw_trade['Direction'].strip(),
                price = float(raw_trade['Price'].replace(' ' + broker.currency,' ')),
                comission = float(raw_trade['Commission'].replace(' ' + broker.currency,' ')),
                tax = float(raw_trade['Charges and fees'].replace(' ' + broker.currency,' ')),
                order_type = raw_trade['Order Type'].strip(),
                execution_venue = raw_trade['Execution venue'].strip(),
                exchange_rate = float(raw_trade['Exchange rate']),
                timestamp = dt.datetime.combine(date, time),
                statement_id = statement.id
            )
        trades: List[Trade] = []
        while '*' not in lines[index]:
            raw_trade = {}
            for key in trade_keys:
                raw_trade[key] = lines[index]
                index += 1
            trades.append(get_trade(raw_trade))
        return trades
    return broker, statement, get_trades(body_lines)
