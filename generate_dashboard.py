import csv
import os
import json

TRADES_FILE = "logs/trades.csv"
SUMMARY_FILE = "logs/daily_summary.csv"
OUTPUT_FILE = "dashboard.html"

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def build_dashboard():
    trades = read_csv(TRADES_FILE)
    summary = read_csv(SUMMARY_FILE)

    if not trades:
        trades = [
            {"Timestamp": "Demo Trade", "Symbol": "AAPL", "Side": "BUY",
             "Qty": "10", "Entry Price": "182.5", "Exit Price": "185.0", "PnL": "+25.00", "Capital After": "10025.00", "Reason": "Demo"}
        ]

    starting_capital = float(summary[0]["Starting Capital"]) if summary else 10000
    latest_capital = float(summary[-1]["Ending Capital"]) if summary else (
        float(trades[-1]["Capital After"]) if trades[-1]["Capital After"] not in ("-", "") else starting_capital
    )
    total_pnl = latest_capital - starting_capital
    pnl_pct = (total_pnl / starting_capital * 100) if starting_capital else 0

    capital_curve = [starting_capital]
    for t in trades:
        try:
            capital_curve.append(float(t["Capital After"]))
        except (ValueError, KeyError):
            pass

    trade_rows_html = ""
    for t in reversed(trades[-30:]):
        side = t.get("Side", "-")
        pnl_raw = t.get("PnL", "0")
        try:
            pnl_val = float(pnl_raw)
        except ValueError:
            pnl_val = 0
        pnl_color = "#22c55e" if pnl_val >= 0 else "#ef4444"
        side_color = "#22c55e" if side == "BUY" else "#ef4444"
        trade_rows_html += f"""
        <div class="trade-row">
          <div>
            <div class="symbol">{t.get('Symbol','-')}</div>
            <div class="ts">{t.get('Timestamp','-')}</div>
          </div>
          <div class="side" style="color:{side_color}">{side}</div>
          <div class="qty">{t.get('Qty','-')}</div>
          <div class="pnl" style="color:{pnl_color}">{pnl_raw}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Algo Trading Dashboard</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 14px; background: #0b0f19; color: #f8fafc;
    font-family: -apple-system, Roboto, sans-serif;
  }}
  .card {{ background: #131b2e; border-radius: 10px; padding: 14px; margin-bottom: 10px; border: 1px solid #1e293b; }}
  .label {{ font-size: 11px; color: #94a3b8; }}
  .big {{ font-size: 24px; font-weight: bold; margin-top: 4px; }}
  .green {{ color: #22c55e; }}
  .red {{ color: #ef4444; }}
  canvas {{ width: 100%; height: 140px; }}
  .trade-row {{
    display: grid; grid-template-columns: 2fr 1fr 1fr 1fr;
    align-items: center; padding: 8px 0; border-bottom: 1px solid #1e293b;
    font-size: 12px;
  }}
  .symbol {{ font-weight: bold; }}
  .ts {{ font-size: 10px; color: #94a3b8; }}
  .side {{ font-weight: bold; text-align: center; }}
  .qty {{ text-align: center; color: #cbd5e1; }}
  .pnl {{ text-align: right; font-weight: bold; }}
  h1 {{ font-size: 15px; margin: 0 0 10px; font-weight: bold; }}
</style>
</head>
<body>

  <h1>🌍 Algo Trading Dashboard</h1>

  <div class="card">
    <div class="label">Current Capital</div>
    <div class="big">${latest_capital:,.2f}</div>
    <div class="{'green' if total_pnl >= 0 else 'red'}" style="font-size:12px; margin-top:2px;">
      {'+' if total_pnl >= 0 else ''}${total_pnl:,.2f} ({pnl_pct:+.2f}%)
    </div>
  </div>

  <div class="card">
    <div class="label" style="margin-bottom:6px;">Capital Curve</div>
    <canvas id="curve"></canvas>
  </div>

  <div class="card">
    <div class="label" style="margin-bottom:4px;">Recent Trades</div>
    {trade_rows_html}
  </div>

<script>
const data = {json.dumps(capital_curve)};
const canvas = document.getElementById('curve');
const ctx = canvas.getContext('2d');
function draw() {{
  const w = canvas.clientWidth, h = 140;
  canvas.width = w * devicePixelRatio; canvas.height = h * devicePixelRatio;
  ctx.scale(devicePixelRatio, devicePixelRatio);
  ctx.clearRect(0,0,w,h);
  if (data.length < 2) return;
  const min = Math.min(...data), max = Math.max(...data);
  const pad = (max - min) * 0.1 || 1;
  const lo = min - pad, hi = max + pad;
  const up = data[data.length-1] >= data[0];
  ctx.strokeStyle = up ? '#22c55e' : '#ef4444';
  ctx.lineWidth = 2;
  ctx.beginPath();
  data.forEach((v, i) => {{
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - lo) / (hi - lo)) * h;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  }});
  ctx.stroke();
}}
draw();
window.addEventListener('resize', draw);
</script>

</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"[dashboard] Successfully generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_dashboard()
