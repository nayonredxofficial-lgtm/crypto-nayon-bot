import requests
import time
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- আপনার নিজস্ব ইনফরমেশনগুলো নিচে নিখুঁতভাবে বসান ---
RAPIDAPI_KEY = "2552f72538msh20ef2ab62659cf5p163fd9jsnce566284437f" 
TELEGRAM_TOKEN = "8997912823:AAFP1SICmh3hc6MLcFW6R1iptuBUp3n5s10" 
TELEGRAM_CHAT_ID = "8997912823" 

# API কনফিগারেশন
URL = "https://binance-futures-signals-ai-trading-bot-crypto-alerts.p.rapidapi.com/generateSignal"
HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "binance-futures-signals-ai-trading-bot-crypto-alerts.p.rapidapi.com"
}

CRYPTO_SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "ADA", "FIL"]

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(telegram_url, json=payload, timeout=15)
        print("✅ Telegram Message Sent Successfully!")
    except Exception as e:
        print("❌ Telegram send error:", e)

# Render এর পোর্ট বাইন্ডিং এরর দূর করার জন্য ডামী ওয়েব সার্ভার
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Crypto Nayon Bot Engine is Running!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    print(f"🖥️ Dummy Web Server active on port {port}")
    server.serve_forever()

def crypto_bot_loop():
    print("⚙️ CRYPTO NAYON BOT ENGINE IS ONLINE ON RENDER... ⚙️")
    while True:
        for symbol in CRYPTO_SYMBOLS:
            payload = {"symbol": symbol}
            querystring = {"language": "en", "noqueue": "1"}
            
            try:
                print(f"📡 Requesting Data for: {symbol}")
                response = requests.post(URL, json=payload, headers=HEADERS, params=querystring, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        result = data.get("result", {})
                        
                        pair = result.get("symbol", f"{symbol}/USDT")
                        direction = result.get("direction", "N/A").upper()
                        entry = result.get("entry", "N/A")
                        stop_loss = result.get("stop_loss") or result.get("stopLoss", "N/A")
                        leverage = result.get("leverage", "N/A")
                        comment = result.get("comment", "No analysis provided.")
                        
                        tp_list = result.get("takeProfit", [])
                        tp_text = ""
                        for i, tp_obj in enumerate(tp_list, 1):
                            tp_val = tp_obj.get(f"TP{i}", "N/A")
                            tp_text += f" ├ Target 0{i} ➔ {tp_val}\n"
                        
                        if "LONG" in direction:
                            header_tag = "🟩  🔹 🅲🆁🆈🅿️🆃🅾️ 🅽🅰️🆈🅾️🅽 🔹  🟩\n╔════════════════════╗\n     🟢 FUTURES: LONG (BUY) 🟢\n╚════════════════════╝"
                            trend_emoji = "📈"
                        else:
                            header_tag = "🟥  🔹 🅲🆁🆈🅿️🆃🅾️ 🅽🅰️🆈🅾️🅽 🔹  🟥\n╔════════════════════╗\n     🔴 FUTURES: SHORT (SELL) 🔴\n╚════════════════════╝"
                            trend_emoji = "📉"
                        
                        msg = (
                            f"{header_tag}\n\n"
                            f"🪙 *Asset:* {pair}\n"
                            f"⚙️ System: AI Predictive Engine\n"
                            f"⚡ *Leverage:* {leverage}\n\n"
                            f"💎 *ENTRY POINT*\n"
                            f" └─> {entry} {trend_emoji}\n\n"
                            f"🎯 *TAKE PROFIT TARGETS*\n"
                            f"{tp_text}\n"
                            f"🛡️ *STOP LOSS (RISK)*\n"
                            f" └─> {stop_loss} ⚠️\n\n"
                            f"📝 *AI MARKET ANALYSIS*\n"
                            f"{comment}\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🤖 @crypto_nayon_Aibot • Automated Alerts\n"
                            f"👨‍💻 *Developer:* @nayondev"
                        )
                        
                        send_telegram_message(msg)
                    else:
                        print(f"❌ API Error for {symbol}: {data.get('message')}")
                else:
                    print(f"⚠️ RapidAPI Status Error {symbol}: {response.status_code}")
                    
            except Exception as e:
                print(f"💥 Loop Error for {symbol}: {e}")
                
            time.sleep(8)
            
        print("😴 Batch complete. Resting for 5 minutes...")
        time.sleep(300)

if _name_ == "_main_":
    Thread(target=run_health_server, daemon=True).start()
    crypto_bot_loop()
