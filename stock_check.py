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

    # S&P500
    if sp500 is not None:
        if sp500 > 0.5:
            score += 1
        elif sp500 < -0.5:
            score -= 1

    # WTI
    if wti is not None:
        if wti > 2:
            score -= 1
        elif wti < -2:
            score += 1

    # USD/JPY
    if usd is not None:
        if usd > 0.3:
            score += 1
        elif usd < -0.3:
            score -= 1

    # 判定
    if score >= 2:
        result = "📈 買い日"
    elif score <= -1:
        result = "📉 回避"
    else:
        result = "🤔 様子見"

    return result, sp500, wti, usd, score


@app.route("/")
def home():
    result, sp500, wti, usd, score = analyze()

    def fmt(x):
        return "N/A" if x is None else f"{x:+.2f}%"

    html = f"""
    <h1>{result}</h1>
    <h3>指標</h3>
    <ul>
        <li>S&P500: {fmt(sp500)}</li>
        <li>WTI原油: {fmt(wti)}</li>
        <li>USD/JPY: {fmt(usd)}</li>
    </ul>
    <h3>Score: {score}</h3>
    """

    return html


if __name__ == "__main__":
    app.run()
