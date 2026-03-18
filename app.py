from flask import Flask
import yfinance as yf

app = Flask(__name__)

def get_change(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d", progress=False)
        if data.empty:
            return None
        close = data["Close"].squeeze().dropna()
        if len(close) < 2:
            return None
        return float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100)
    except:
        return None

def analyze():
    sp500 = get_change("^GSPC")
    wti = get_change("CL=F")
    usd = get_change("JPY=X")

    score = 0

    if sp500 and sp500 > 0.5:
        score += 1
    elif sp500 and sp500 < -0.5:
        score -= 1

    if wti and wti > 2:
        score -= 1
    elif wti and wti < -2:
        score += 1

    if usd and usd > 0.3:
        score += 1
    elif usd and usd < -0.3:
        score -= 1

    if score >= 2:
        return "📈 買い日"
    elif score <= -1:
        return "📉 回避"
    return "🤔 様子見"

@app.route("/")
def home():
    result = analyze()
    return f"<h1>{result}</h1><p>株式市場判定</p>"

if __name__ == "__main__":
    app.run()