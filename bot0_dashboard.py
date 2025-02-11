from config import config
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from textblob import TextBlob
import praw
import yfinance as yf
import requests

# Credenciais
config = {
    "binance_api_key": "jbxQyBlNmDpZLuW3fGVs3eLsLQAAbZJJCBTdz5cBFVyBEpg7HhEfxmDfm8cxCK12",
    "binance_api_secret": "qevwzp7iArNsitgjm6DVbRsl3cGswUAeDnPuvi1PgvaXRlZXF2G07KIarJ4HXbh1",
    "coingecko_api_key": "CG-iSGAPZYuWiVkBgKw9R41XnUk",
    "reddit_client_id": "vF-byer6LtI0eU1OKk1VLw",
    "reddit_client_secret": "pea_3JrPKrHxI2AI8Mto4FZQ8fuRpA",
    "reddit_user_agent": "bot ai for crypto"
}

# Conexão com a Testnet da Binance
client = Client(api_key=config["binance_api_key"], api_secret=config["binance_api_secret"])
client.API_URL = "https://testnet.binance.vision/api"

# Lista dos 10 pares mais usados
pares_populares = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
    "SOL-USD", "DOGE-USD", "MATIC-USD", "DOT-USD", "SHIB-USD"
]

# Função para obter dados históricos do yfinance
def obter_dados_yfinance(simbolo, intervalo="1d", quantidade="30d"):
    try:
        dados = yf.download(tickers=simbolo, period=quantidade, interval=intervalo)
        return dados.reset_index()
    except Exception as e:
        return pd.DataFrame({"Erro": [f"Erro ao carregar {simbolo}: {str(e)}"]})

# Função para obter dados de mercado do CoinGecko
def obter_dados_coingecko():
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano,binancecoin&vs_currencies=usd&include_24hr_change=true"
    headers = {"Authorization": f"Bearer {config['coingecko_api_key']}"}
    response = requests.get(url, headers=headers).json()
    
    dados = []
    for cripto, info in response.items():
        dados.append({
            "Cripto": cripto.capitalize(),
            "Preço Atual (USD)": info["usd"],
            "Alteração 24h (%)": round(info["usd_24h_change"], 2) if "usd_24h_change" in info else "N/A"
        })
    return pd.DataFrame(dados)

# Função para analisar sentimentos no Reddit
def analisar_sentimentos_reddit(termo):
    subreddit = reddit.subreddit("cryptocurrency")
    comentarios = subreddit.search(termo, limit=50)
    
    polaridade_total = 0
    total = 0
    for comentario in comentarios:
        if hasattr(comentario, "selftext"):
            analise = TextBlob(comentario.selftext)
            polaridade_total += analise.sentiment.polarity
            total += 1

    return round(polaridade_total / total, 2) if total > 0 else "Sem Dados"

# Função para exibir gráfico
def exibir_grafico(dados, simbolo):
    plt.figure(figsize=(10, 5))
    plt.plot(dados["Close"], label=f"Fechamento {simbolo}")
    plt.title(f"Gráfico de Preços - {simbolo}")
    plt.legend()
    st.pyplot(plt)

# Painel do Bot0
st.title("Bot0 - Painel de Trading (Binance + CoinGecko + yfinance + Reddit)")

# Dados do CoinGecko
st.header("Análise de Criptomoedas (CoinGecko)")
dados_coingecko = obter_dados_coingecko()
st.dataframe(dados_coingecko)

# Dados do yfinance para os 10 pares
st.header("Dados Históricos do yfinance (10 Pares Mais Usados)")
for simbolo in pares_populares:
    st.subheader(f"Dados Históricos: {simbolo}")
    dados_yfinance = obter_dados_yfinance(simbolo=simbolo)
    if not dados_yfinance.empty and "Erro" not in dados_yfinance:
        st.dataframe(dados_yfinance[["Date", "Close"]])  # Mostrar apenas data e fechamento
        exibir_grafico(dados_yfinance, simbolo)
    else:
        st.error(f"Erro ao carregar dados para {simbolo}.")

# Conexão com o Reddit
reddit = praw.Reddit(
    client_id=config["reddit_client_id"],
    client_secret=config["reddit_client_secret"],
    user_agent=config["reddit_user_agent"]
)

# Sentimento do Reddit
st.header("Análise de Sentimento no Reddit")
for termo in ["Bitcoin", "Ethereum", "Cardano", "Binance Coin"]:
    sentimento = analisar_sentimentos_reddit(termo)
    st.write(f"Sentimento sobre {termo}: {'Positivo' if sentimento > 0 else 'Negativo' if sentimento < 0 else 'Neutro'} ({sentimento})")
    