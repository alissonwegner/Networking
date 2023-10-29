from flask import Flask, render_template
import requests
import pandas as pd
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    key = "WJ552P5K6CBZRY2V"
    acoes = ['ITUB4', 'ABEV3', 'BBAS3', 'MXRF11', 'MCHF11']
    compilada = pd.DataFrame()
    
    for acao in acoes:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={acao}.SAO&apikey={key}&datatype=csv'
        r = requests.get(url)
        tabela = pd.read_csv(StringIO(r.text))
        lista_tabelas = [compilada, tabela]
        compilada = pd.concat(lista_tabelas)
    
    data = compilada.to_html(classes="table table-bordered table-striped", index=False)
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
