import requests
import pandas as pd
from io import StringIO
key = "WJ552P5K6CBZRY2V"
url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=itau&apikey={key}&datatype=csv'
r = requests.get(url)
#print(r.text)
tabela = pd.read_csv(StringIO(r.text))
    
print(tabela)
