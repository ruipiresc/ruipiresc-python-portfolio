from dotenv import load_dotenv
load_dotenv()

import fire
from portfolio import Portfolio

if __name__ == '__main__':
  fire.Fire(Portfolio)