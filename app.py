import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Algo Trading Bot"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK

    # UI Elements
    status_text = ft.Text("Connecting to Bot...", color=ft.colors.GREEN_ACCENT, size=16, weight=ft. FontWeight.BOLD)
    capital_text = ft.Text("Capital: --", color=ft.colors.WHITE, size=18)
    trade_text = ft.Text("Active Trade: --", color=ft.colors.AMBER, size=14)
    target_text = ft.Text("Target: --", color=ft.colors.BLUE_ACCENT, size=14)
    sl_text = ft.Text("Stop Loss: --", color=ft.colors.RED_ACCENT, size=14)
    pnl_text = ft.Text("P&L: --", color=ft.colors.WHITE, size=16)

    def fetch_data(e):
        try:
            response = requests.get("http://127.0.0.1:8000/status")
            if response.status_code == 200:
                data = response.json()
                status_text.value = "Status: Online (Connected)"
                capital_text.value = f"Capital: ₹{data.get('capital')}"
                trade_text.value = f"Active Trade: {data.get('active_trade')}"
                target_text.value = f"Target: {data.get('target')}"
                sl_text.value = f"Stop Loss: {data.get('stop_loss')}"
                pnl_text.value = f"P&L: {data.get('pnl')}"
            else:
                status_text.value = "Status: Server Error"
        except Exception as ex:
            status_text.value = "Status: Disconnected from Server"
        page.update()

    refresh_btn = ft.ElevatedButton("Refresh Status", on_click=fetch_data, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("🚀 Algo Trading Dashboard", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Divider(color=ft.colors.GREY),
                status_text,
                capital_text,
                trade_text,
                target_text,
                sl_text,
                pnl_text,
                ft.SizedBox(height=20),
                refresh_btn
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START),
            padding=20,
            bgcolor=ft.colors.GREY_900,
            border_radius=10
        )
    )

    # Automatically fetch data on start
    fetch_data(None)

ft.app(target=main)
