import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

# ===== 設定 =====
FROM_EMAIL = "takamis0318@gmail.com"
APP_PASSWORD = "adsxufyiflsloqau"
TO_EMAIL = "takamis0318@gmail.com"

TICKERS = {
    "sp500": "^GSPC",
    "wti": "CL=F",
    "usd": "JPY=X",
    "nikkei": "^N225"  # 安定版（日経現物）
}

# ===== データ取得（完全安全版） =====
def get_change(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d", progress=False)

        # データなし
        if data.empty:
            return None

        close = data["Close"]

        # DataFrame→Series対策
        close = close.squeeze()

        # NaN除去
        close = close.dropna()

        # データ不足
        if len(close) < 2:
            return None

        # 変化率（float保証）
        change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
        return float(change)

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# ===== スコア計算 =====
def add_score(value, pos_th, neg_th):
    if value is None:
        return 0

    if not isinstance(value, (int, float)):
        return 0

    if value > pos_th:
        return 1
    elif value < neg_th:
        return -1
    return 0

# ===== データ取得 =====
sp500 = get_change(TICKERS["sp500"])
wti = get_change(TICKERS["wti"])
usd = get_change(TICKERS["usd"])
nikkei = get_change(TICKERS["nikkei"])

# ===== スコア =====
score = 0

score += add_score(sp500, 0.5, -0.5)

# 原油は逆指標
if wti is not None:
    if wti > 2:
        score -= 1
    elif wti < -2:
        score += 1

score += add_score(usd, 0.3, -0.3)

# 日経は補助的
score += add_score(nikkei, 0.5, -0.5)

# ===== 地雷チェック =====
danger = False

if (wti is not None and wti > 3) or (sp500 is not None and sp500 < -1.5):
    danger = True

# ===== 判定 =====
if danger:
    result = "⚠️ 地雷日：ノートレ推奨"
elif score >= 2:
    result = "📈 買い日"
elif score <= -1:
    result = "📉 売り or 回避"
else:
    result = "🤔 様子見"

# ===== 表示整形 =====
def fmt(x):
    return f"{x:.2f}%" if isinstance(x, (int, float)) else "N/A"

# ===== メッセージ =====
message = f"""
【本日の自動判定】

S&P500: {fmt(sp500)}
WTI原油: {fmt(wti)}
USD/JPY: {fmt(usd)}
日経平均: {fmt(nikkei)}

スコア: {score}
判定: {result}
"""

# ===== メール送信 =====
def send_mail(body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = f"【{result}】株式市場"
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Date"] = formatdate()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(FROM_EMAIL, APP_PASSWORD)
            server.send_message(msg)

        print("メール送信成功")

    except Exception as e:
        print(f"メール送信エラー: {e}")

# ===== 実行 =====
if __name__ == "__main__":
    send_mail(message)