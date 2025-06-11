# main.py
# --------------------------------------------------------------------------
#  Mission Dashboard launcher with persistent page caching, clean logout,
#  and graceful shutdown of telemetry thread
#  © 2025  Arbalest Rocketry
# --------------------------------------------------------------------------

import tkinter as tk
from login_page import LoginPage
from dashboard_page import DashboardPage
from plotting_page import PlottingPage
from gps_page import GPSPage
from analytics_page import AnalyticsPage
from telemetry_udp import Telemetry
from intro_page import show_intro_popup

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arbalest Rocketry Mission Dashboard")
        self.state("zoomed")
        self.configure(bg="#171e24")
        # Ensure telemetry thread is closed on exit
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # User and telemetry
        self.user = {"name": "", "callsign": ""}
        self.telemetry = Telemetry()

        # Cached page instances
        self.pages = {}
        self.current_page = None

        # Sidebar navigation
        self._build_sidebar()

        # Main content container
        self.container = tk.Frame(self, bg="#171e24")
        self.container.pack(side="right", fill="both", expand=True)

        # Start at login
        self.show_page("login")

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg="#101e34", width=60)
        self.sidebar.pack(side="left", fill="y")
        self.btns = {}
        # (icon, key, command)
        nav = [
            ("🏠", "dashboard", lambda: self.show_page("dashboard")),
            ("📊", "plotting", lambda: self.show_page("plotting")),
            ("🗺", "gps",      lambda: self.show_page("gps")),
            ("🧮", "analytics",lambda: self.show_page("analytics")),
            ("ℹ", "intro",    show_intro_popup),
            ("🔒", "logout",  lambda: self.show_page("logout")),
        ]
        for idx, (icon, key, cmd) in enumerate(nav):
            btn = tk.Button(
                self.sidebar, text=icon, font=("Consolas", 22), width=3,
                bg="#101e34", fg="#00f0ff", activebackground="#263344",
                bd=0, command=cmd
            )
            btn.pack(pady=(22 if idx == 0 else 10))
            self.btns[key] = btn

    def show_page(self, page: str):
        # Handle logout as a reset to login
        if page == "logout":
            self.user = {"name": "", "callsign": ""}
            self.telemetry.reset()
            page = "login"

        # Hide current page
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].pack_forget()

        # Create page if not cached
        if page not in self.pages:
            if page == "login":
                self.pages[page] = LoginPage(self.container, self.login_success)
            elif page == "dashboard":
                self.pages[page] = DashboardPage(self.container, self.telemetry, self.user)
            elif page == "plotting":
                self.pages[page] = PlottingPage(self.container, self.telemetry, self.user)
            elif page == "gps":
                self.pages[page] = GPSPage(self.container, self.telemetry, self.user)
            elif page == "analytics":
                self.pages[page] = AnalyticsPage(self.container, self.telemetry, self.user)
            else:
                return  # unknown key
        # Show the requested page
        frame = self.pages[page]
        frame.pack(fill="both", expand=True)
        self.current_page = page
        # Update sidebar button highlight
        self._highlight_nav(page)

    def _highlight_nav(self, key: str):
        for name, btn in self.btns.items():
            btn.config(bg="#101e34")
        if key in self.btns:
            self.btns[key].config(bg="#263344")

    def login_success(self, name: str, callsign: str):
        self.user["name"] = name
        self.user["callsign"] = callsign
        self.show_page("dashboard")

    def _on_close(self):
        # Clean shutdown of telemetry
        try:
            self.telemetry.close()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    MainApp().mainloop()

