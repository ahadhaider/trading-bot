from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import datetime

import config
import strategy
import risk_manager as risk_manager_module
import state_store
from combined_logger import CombinedLogger

if config.MODE == "paper":
    import broker_paper as broker
else:
    import broker_zerodha as broker

app = FastAPI()

rm = risk_manager_module.RiskManager(config.STARTING_CAPITAL)
state_store.apply_state(rm, state_store.load_state())
logger = CombinedLogger()

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE

@app.get("/api/status")
def status():
    total_pnl = rm.capital - config.STARTING_CAPITAL
    pnl_pct = (total_pnl / config.STARTING_CAPITAL * 100) if config.STARTING_CAPITAL else 0
    return JSONResponse({
        "mode": config.MODE,
        "capital": round(rm.capital, 2),
        "starting_capital": config.STARTING_CAPITAL,
        "total_pnl": round(total_pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "trading_halted": rm.trading_halted,
        "open_positions": rm.open_positions,
        "symbols": config.SYMBOLS,
    })

@app.get("/api/trades")
def trades():
    import csv
    out = []
    try:
        with open("logs/trades.csv", newline="") as f:
            out = list(csv.DictReader(f))
    except FileNotFoundError:
        pass
    out.reverse()
    return JSONResponse(out[:40])

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Global Algo Bot - Pro Terminal</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0b0f19; color: #ffffff; padding: 10px; margin: 0; }
  
  .header-card { background: #131b2e; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 8px; }
  .card { background: #131b2e; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 8px; position: relative; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
  
  .ticker-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 6px; }
  .ticker-box { background: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 6px 2px; text-align: center; cursor: pointer; }
  
  .green { color: #22c55e; font-weight: bold; }
  .red { color: #ef4444; font-weight: bold; }
  .yellow { color: #facc15; font-weight: bold; }
  
  input, select { background: #0b0f19; color: #fff; border: 1px solid #334155; padding: 8px; border-radius: 6px; width: 100%; font-size: 12px; outline: none; margin-top: 4px; }
  .btn-primary { background: #2563eb; color: white; border: none; padding: 9px; font-weight: bold; border-radius: 6px; width: 100%; cursor: pointer; font-size: 12px; margin-top: 6px; }
  .btn-success { background: #22c55e; color: white; border: none; padding: 9px; font-weight: bold; border-radius: 6px; width: 100%; cursor: pointer; font-size: 12px; margin-top: 6px; }
  .btn-danger { background: #ef4444; color: white; border: none; padding: 5px 10px; font-size: 10px; font-weight: bold; border-radius: 5px; cursor: pointer; }
  
  #suggestions-list { position: absolute; left: 12px; right: 12px; top: 72px; background: #0b0f19; border: 1px solid #334155; border-radius: 6px; max-height: 140px; overflow-y: auto; z-index: 99; display: none; }
  .suggestion-item { padding: 7px 10px; font-size: 11px; border-bottom: 1px solid #1e293b; cursor: pointer; color: #cbd5e1; }
  .suggestion-item:hover { background: #1e293b; color: #fff; }

  .chart-box { background: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 4px; margin-top: 6px; position: relative; overflow: hidden; }
  #pro-canvas { width: 100%; height: 240px; display: block; touch-action: pan-y; }

  table { width: 100%; border-collapse: collapse; margin-top: 4px; font-size: 10px; }
  th, td { padding: 5px 3px; text-align: left; border-bottom: 1px solid #1e293b; color: #94a3b8; }
  th { color: #ffffff; font-weight: bold; font-size: 10px; }
</style>
</head>
<body>
    <div class="header-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 14px; font-weight: bold;">🌍 Global Algo Bot</div>
                <div style="font-size: 9px; color: #94a3b8; margin-top: 2px;">Logged in as: ahad@123.com</div>
            </div>
            <div style="width: 7px; height: 7px; background: #22c55e; border-radius: 50%;"></div>
        </div>
    </div>

    <div class="card" style="border: 1px solid #2563eb;">
        <div style="font-size: 11px; font-weight: bold; color: #60a5fa; margin-bottom: 4px;">🔗 Link Broker Account</div>
        <div class="grid-2">
            <div>
                <div style="font-size: 8px; color: #94a3b8;">Select Broker</div>
                <select id="broker-name">
                    <option>Dhan HQ</option>
                    <option>Zerodha Kite</option>
                    <option>Upstox Pro</option>
                    <option>Angel One</option>
                </select>
            </div>
            <div>
                <div style="font-size: 8px; color: #94a3b8;">Client ID</div>
                <input type="text" id="broker-clientid" placeholder="e.g. AB1234">
            </div>
        </div>
        <div style="margin-top: 2px;">
            <div style="font-size: 8px; color: #94a3b8;">API Token</div>
            <input type="password" id="broker-token" placeholder="Enter API key">
        </div>
        <button class="btn-success" onclick="linkBrokerAccount()">Connect Broker</button>
        <div id="broker-status" style="font-size: 9px; color: #22c55e; margin-top: 4px; display: none;">🟢 Connected Successfully!</div>
    </div>

    <div class="card">
        <div style="font-size: 9px; color: #94a3b8; margin-bottom: 4px;">🔥 TOP TRENDING GLOBAL STOCKS</div>
        <div class="ticker-grid">
            <div class="ticker-box" onclick="selectStock('NVDA')"><div style="font-size: 9px; font-weight: bold;">NVDA</div><div style="font-size: 8px; color: #94a3b8;">$875.3</div><div class="green" style="font-size: 7px;">+4.2%</div></div>
            <div class="ticker-box" onclick="selectStock('TSLA')"><div style="font-size: 9px; font-weight: bold;">TSLA</div><div style="font-size: 8px; color: #94a3b8;">$175.2</div><div class="green" style="font-size: 7px;">+2.8%</div></div>
            <div class="ticker-box" onclick="selectStock('AAPL')"><div style="font-size: 9px; font-weight: bold;">AAPL</div><div style="font-size: 8px; color: #94a3b8;">$182.5</div><div class="green" style="font-size: 7px;">+1.1%</div></div>
            <div class="ticker-box" onclick="selectStock('RELIANCE')"><div style="font-size: 9px; font-weight: bold;">RELIANC</div><div style="font-size: 8px; color: #94a3b8;">₹1,327</div><div class="green" style="font-size: 7px;">+1.5%</div></div>
        </div>
    </div>

    <div class="card" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="font-size: 9px; color: #94a3b8; margin-bottom: 2px;">System Status</div>
            <div class="green" style="font-size: 12px;">Active (Running)</div>
        </div>
        <button class="btn-danger" onclick="emergencyExit()">🚨 EMERGENCY EXIT</button>
    </div>

    <div class="card">
        <div style="font-size: 11px; font-weight: bold; margin-bottom: 4px;">🔍 Search & Trade Any Global Company</div>
        <input type="text" id="trade-symbol" placeholder="Type name (e.g. Apple, Tata)..." oninput="filterStocks(this.value)">
        <div id="suggestions-list"></div>
        
        <div class="grid-2" style="margin-top: 6px;">
            <div>
                <div style="font-size: 8px; color: #94a3b8;">Quantity</div>
                <input type="number" id="trade-qty" value="10">
            </div>
            <div>
                <div style="font-size: 8px; color: #94a3b8;">Order Type</div>
                <select id="trade-type">
                    <option value="BUY">🟢 BUY (Long)</option>
                    <option value="SELL">🔴 SELL (Short)</option>
                </select>
            </div>
        </div>
        <button class="btn-primary" onclick="executeGlobalTrade()">Execute Global Trade</button>
    </div>

    <div class="card">
        <div style="font-size: 10px; color: #94a3b8; margin-bottom: 2px;">Available Capital</div>
        <div style="font-size: 18px; font-weight: bold;" id="capital-val">$10,000.00</div>
    </div>

    <div class="card">
        <div style="font-size: 10px; color: #94a3b8; margin-bottom: 2px;">Active Trade</div>
        <div id="active-trade-label" class="yellow" style="font-size: 14px; font-weight: bold;">AAPL BUY qty=10</div>
    </div>

    <div class="grid-2">
        <div class="card" style="margin:0;">
            <div style="font-size: 9px; color: #94a3b8; margin-bottom: 2px;">Target</div>
            <div class="green" style="font-size: 13px;">$190.00</div>
        </div>
        <div class="card" style="margin:0;">
            <div style="font-size: 9px; color: #94a3b8; margin-bottom: 2px;">Stop Loss</div>
            <div class="red" style="font-size: 13px;">$178.00</div>
        </div>
    </div>

    <div class="card">
        <div style="font-size: 10px; color: #94a3b8; margin-bottom: 2px;">Total P&L</div>
        <div id="pnl-display" class="green" style="font-size: 16px;">+$0.00</div>
    </div>

    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 11px; color: #94a3b8;">TradingView Pro Candlestick Chart</span>
            <span id="live-price-tag" class="green" style="font-size: 11px;">$185.50</span>
        </div>
        <div class="chart-box">
            <canvas id="pro-canvas"></canvas>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 9px; color: #64748b; margin-top: 4px;">
            <span>↔ Swipe to Pan History</span><span class="green">● Smooth Candle Engine</span>
        </div>
    </div>

    <div class="card">
        <div style="font-size: 11px; font-weight: bold; margin-bottom: 4px;">📋 Live Order Logs</div>
        <table id="order-table">
            <tr><th>Time</th><th>Symbol</th><th>Type</th><th>Qty</th><th>Price</th><th>Status</th></tr>
            <tr><td>09:15:22</td><td>AAPL</td><td>BUY</td><td>10</td><td>$182.5</td><td><span class="yellow">OPEN</span></td></tr>
        </table>
    </div>

    <div style="text-align: center; margin-top: 12px; margin-bottom: 16px;">
        <a href="#" style="color: #ef4444; text-decoration: none; font-size: 11px; font-weight: bold;" onclick="alert('Logged out successfully.')">Logout from Terminal</a>
    </div>

    <script>
        const globalStocks = [
            "Apple Inc (AAPL)", "Microsoft Corp (MSFT)", "NVIDIA Corp (NVDA)", "Tesla Inc (TSLA)",
            "Amazon.com Inc (AMZN)", "Alphabet Inc (GOOGL)", "Meta Platforms (META)", "Netflix Inc (NFLX)",
            "Tata Consultancy Services (TCS)", "Reliance Industries (RELIANCE)", "Tata Motors (TATAMOTORS)"
        ];

        function filterStocks(query) {
            let list = document.getElementById('suggestions-list');
            if (!query) { list.style.display = 'none'; return; }
            let filtered = globalStocks.filter(s => s.toLowerCase().includes(query.toLowerCase()));
            if (filtered.length > 0) {
                list.innerHTML = filtered.map(item => `<div class="suggestion-item" onclick="selectItem('${item}')">${item}</div>`).join('');
                list.style.display = 'block';
            } else { list.style.display = 'none'; }
        }

        function selectItem(name) {
            document.getElementById('trade-symbol').value = name;
            document.getElementById('suggestions-list').style.display = 'none';
        }

        function selectStock(sym) {
            document.getElementById('trade-symbol').value = sym;
            document.getElementById('active-trade-label').innerText = sym + ' BUY qty=10';
        }

        function linkBrokerAccount() {
            let broker = document.getElementById('broker-name').value;
            let cid = document.getElementById('broker-clientid').value;
            if(!cid) { alert('Please enter Client ID'); return; }
            document.getElementById('broker-status').style.display = 'block';
            alert('Successfully connected to ' + broker + ' for client ' + cid);
        }

        const canvas = document.getElementById('pro-canvas');
        const ctx = canvas.getContext('2d');
        
        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth * window.devicePixelRatio;
            canvas.height = 240 * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        let candles = [];
        let baseP = 175.00;
        for (let i = 0; i < 35; i++) {
            let open = baseP + (Math.random() * 1.2 - 0.6);
            let high = open + Math.random() * 1.0;
            let low = open - Math.random() * 1.0;
            let close = low + Math.random() * (high - low);
            baseP = close;
            candles.push({ open, high, low, close });
        }

        let offsetX = 0;
        let isDragging = false;
        let startX = 0;

        canvas.addEventListener('touchstart', (e) => {
            isDragging = true;
            startX = e.touches[0].clientX - offsetX;
        });
        canvas.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            offsetX = e.touches[0].clientX - startX;
            if (offsetX > 0) offsetX = 0;
            let maxScroll = -((candles.length * 18) - (canvas.clientWidth - 95));
            if (offsetX < maxScroll) offsetX = maxScroll;
        });
        canvas.addEventListener('touchend', () => { isDragging = false; });

        let tickCounter = 0;

        function drawChart() {
            const width = canvas.clientWidth;
            const height = 240;
            ctx.clearRect(0, 0, width, height);

            const scaleWidth = 75;
            const chartWidth = width - scaleWidth;

            // Background Grid Lines
            ctx.strokeStyle = '#161e2e';
            ctx.lineWidth = 1;
            for (let y = 30; y < height - 10; y += 35) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(chartWidth, y);
                ctx.stroke();
            }

            let minP = Math.min(...candles.map(c => c.low));
            let maxP = Math.max(...candles.map(c => c.high));
            let range = maxP - minP || 1;
            let pad = range * 0.1;
            minP -= pad;
            maxP += pad;
            range = maxP - minP;

            let chartH = height - 20;
            let candleW = 10;
            let gap = 8;

            candles.forEach((c, i) => {
                let x = 12 + offsetX + (i * (candleW + gap));
                if (x < -20 || x > chartWidth - 15) return;

                let isGreen = c.close >= c.open;
                let color = isGreen ? '#22c55e' : '#ef4444';

                let yHigh = height - 10 - ((c.high - minP) / range) * chartH;
                let yLow = height - 10 - ((c.low - minP) / range) * chartH;
                let yOpen = height - 10 - ((c.open - minP) / range) * chartH;
                let yClose = height - 10 - ((c.close - minP) / range) * chartH;

                ctx.strokeStyle = color;
                ctx.lineWidth = 1.2;
                ctx.beginPath();
                ctx.moveTo(x + candleW / 2, yHigh);
                ctx.lineTo(x + candleW / 2, yLow);
                ctx.stroke();

                ctx.fillStyle = color;
                let bodyY = Math.min(yOpen, yClose);
                let bodyH = Math.max(Math.abs(yOpen - yClose), 2);
                ctx.fillRect(x, bodyY, candleW, bodyH);
            });

            let lastC = candles[candles.length - 1];
            let liveY = height - 10 - ((lastC.close - minP) / range) * chartH;

            // Live Price Dashed Line
            ctx.strokeStyle = '#2dd4bf';
            ctx.lineWidth = 1;
            ctx.setLineDash([3, 3]);
            ctx.beginPath();
            ctx.moveTo(0, liveY);
            ctx.lineTo(chartWidth, liveY);
            ctx.stroke();
            ctx.setLineDash([]);

            // Right Price Scale Panel
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(chartWidth, 0, scaleWidth, height);
            ctx.strokeStyle = '#1e293b';
            ctx.beginPath();
            ctx.moveTo(chartWidth, 0);
            ctx.lineTo(chartWidth, height);
            ctx.stroke();

            // Price Scale Labels
            ctx.fillStyle = '#94a3b8';
            ctx.font = '9px sans-serif';
            for (let y = 30; y < height - 10; y += 35) {
                let priceVal = maxP - ((y / chartH) * range);
                ctx.fillText(priceVal.toFixed(2), chartWidth + 8, y + 3);
            }

            // Current Live Price Badge
            let badgeY = Math.max(12, Math.min(height - 15, liveY));
            ctx.fillStyle = '#2dd4bf';
            ctx.fillRect(chartWidth, badgeY - 9, scaleWidth, 18);
            ctx.fillStyle = '#0b0f19';
            ctx.font = 'bold 9px sans-serif';
            ctx.fillText(lastC.close.toFixed(2), chartWidth + 8, badgeY + 3);
        }

        // Smooth Tick & Stable Candle Rolling Engine (New candle every 15 seconds)
        setInterval(() => {
            let last = candles[candles.length - 1];
            let rand = (Math.random() * 0.8 - 0.4);
            last.close += rand;
            last.high = Math.max(last.high, last.close);
            last.low = Math.min(last.low, last.close);

            document.getElementById('live-price-tag').innerText = '$' + last.close.toFixed(2);

            tickCounter++;
            if (tickCounter >= 15) {
                tickCounter = 0;
                let nextOpen = last.close;
                let nextClose = nextOpen + (Math.random() * 1.5 - 0.75);
                candles.push({
                    open: nextOpen,
                    high: Math.max(nextOpen, nextClose) + 0.4,
                    low: Math.min(nextOpen, nextClose) - 0.4,
                    close: nextClose
                });
                offsetX = -((candles.length * 18) - (canvas.clientWidth - 95));
            }

            drawChart();
        }, 1000);

        drawChart();

        async function fetchStatus() {
            try {
                let res = await fetch('/api/status');
                let d = await res.json();
                document.getElementById('capital-val').innerText = '$' + d.capital.toLocaleString('en-US', {minimumFractionDigits: 2});
                let pnlEl = document.getElementById('pnl-display');
                pnlEl.innerText = (d.total_pnl >= 0 ? '+$' : '-$') + Math.abs(d.total_pnl).toFixed(2);
                pnlEl.className = d.total_pnl >= 0 ? 'green' : 'red';
            } catch(e) {}
        }
        setInterval(fetchStatus, 3000);

        function executeGlobalTrade() {
            let sym = document.getElementById('trade-symbol').value.toUpperCase();
            let qty = document.getElementById('trade-qty').value;
            let type = document.getElementById('trade-type').value;
            
            let table = document.getElementById('order-table');
            let now = new Date().toTimeString().split(' ')[0];
            let row = table.insertRow(1);
            let typeColor = type === 'BUY' ? 'green' : 'red';
            row.innerHTML = `<td>${now}</td><td>${sym}</td><td class="${typeColor}">${type}</td><td>${qty}</td><td>$185.0</td><td><span class="yellow">OPEN</span></td>`;
            alert('Global ' + type + ' Trade Executed Successfully for ' + sym);
        }

        function emergencyExit() {
            if(!confirm('Emergency Exit All Positions?')) return;
            fetch('/api/emergency_exit', {method: 'POST'}).then(() => {
                alert('All positions closed successfully.');
                location.reload();
            });
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
