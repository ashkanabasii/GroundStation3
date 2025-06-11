# dashboard_page.py
# --------------------------------------------------------------------------
#  Live telemetry dashboard page (Tkinter)
#  © 2025  Arbalest Rocketry
# --------------------------------------------------------------------------
import tkinter as tk
from datetime import datetime
from random import uniform
from typing import Dict, Tuple, List

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from tkintermapview import TkinterMapView

from analog_gauge import AnalogGauge
from telemetry_udp import Telemetry   # ← live data source

# ────────────────────────────────────────────────────────────────────────────
class DashboardPage(tk.Frame):
    GAUGE_SIZE = 240
    PLOT_BG    = "#101a25"
    UI_BG      = "#171e24"
    FG_TXT     = "#e0eefa"
    FG_ACCENT  = "#00f0ff"

    # ───────────────────────────────────────────────────────────────────
    def __init__(self, master, telemetry: Telemetry, user: Dict[str, str], **kwargs):
        super().__init__(master, bg=self.UI_BG, **kwargs)
        self.telemetry = telemetry
        self.user      = user
        self.trajectory_coords: List[Tuple[float, float]] = []

        # ===== GRID LAYOUT =================================================
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=1)

        # ===== HEADER (logo | clocks | system health) =====================
        header = tk.Frame(self, bg=self.UI_BG)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(8, 0))
        header.columnconfigure((0, 2), weight=1)
        header.columnconfigure(1, weight=2)

        # --- UTC / LST / callsign block ---
        id_col = tk.Frame(header, bg=self.UI_BG); id_col.grid(row=0, column=0, sticky="w")
        self.utc_label = tk.Label(id_col, font=("Consolas", 13, "bold"),
                                  fg=self.FG_ACCENT, bg=self.UI_BG)
        self.lst_label = tk.Label(id_col, font=("Consolas", 13, "bold"),
                                  fg=self.FG_ACCENT, bg=self.UI_BG)
        self.utc_label.pack(anchor="w"); self.lst_label.pack(anchor="w", pady=(0, 3))
        tk.Label(id_col, text="CALL SIGN:", font=("Consolas", 14, "bold"),
                 fg="#00ffea", bg=self.UI_BG).pack(side="left")
        tk.Label(id_col, text=user.get("callsign", "---"),
                 font=("Consolas", 14, "bold"),
                 fg="#18fff7", bg=self.UI_BG).pack(side="left")

        # --- logo ---
        logo_col = tk.Frame(header, bg=self.UI_BG); logo_col.grid(row=0, column=1)
        try:
            logo_img = Image.open("AB_logo.png").resize((240, 52), Image.LANCZOS)
            logo_tk  = ImageTk.PhotoImage(logo_img)
            logo_lbl = tk.Label(logo_col, image=logo_tk, bg=self.UI_BG)
            logo_lbl.image = logo_tk
        except FileNotFoundError:
            logo_lbl = tk.Label(logo_col, text="ARBALEST",
                                font=("Consolas", 34, "bold"),
                                fg=self.FG_ACCENT, bg=self.UI_BG)
        logo_lbl.pack()

        # --- system-health badge ---
        sys_col = tk.Frame(header, bg=self.UI_BG); sys_col.grid(row=0, column=2, sticky="e")
        self.sys_health = tk.Label(sys_col, text="SYSTEM: OK",
                                   font=("Consolas", 13, "bold"),
                                   fg="#00ff6b", bg=self.UI_BG,
                                   bd=2, relief="ridge", width=16)
        self.sys_health.pack(anchor="e")

        # ===== TELEMETRY NUMBERS (left) ===================================
        telem_panel = tk.Frame(self, bg=self.UI_BG)
        telem_panel.grid(row=1, column=0, sticky="nw", padx=(10, 2))
        self.labels: Dict[str, tk.Label] = {}
        self.data_fields = [("Yaw (deg)", "Yaw"),
                            ("Pitch (deg)", "Pitch"),
                            ("Roll (deg)", "Roll"),
                            ("Altitude (m)", "Alt")]

        for desc, key in self.data_fields:
            row = tk.Frame(telem_panel, bg=self.UI_BG); row.pack(anchor="w")
            tk.Label(row, text=f"{desc}:",
                     font=("Consolas", 17, "bold"),
                     fg=self.FG_TXT, bg=self.UI_BG, width=15, anchor="w").pack(side="left")
            lbl = tk.Label(row, text="---",
                           font=("Consolas", 13),
                           fg="#62e0e7", bg=self.UI_BG,
                           width=9, anchor="w")
            lbl.pack(side="left"); self.labels[key] = lbl

        # ===== MAP (right) ===============================================
        map_panel = tk.Frame(self, bg=self.UI_BG)
        map_panel.grid(row=1, column=1, sticky="nsew", padx=(2, 10))
        map_panel.rowconfigure(0, weight=1); map_panel.columnconfigure(0, weight=1)

        self.map_widget = TkinterMapView(map_panel, width=520, height=260, corner_radius=18)
        self.map_widget.grid(row=0, column=0, sticky="nsew")

        init_lat, init_lon = 43.7735, -79.5015
        self.map_marker = self.map_widget.set_marker(init_lat, init_lon, text="Rocket")
        self.map_widget.set_position(init_lat, init_lon)

        # ===== EVENT LOG ==================================================
        log_frame = tk.Frame(self, bg=self.UI_BG)
        log_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=80, pady=(0, 4))
        tk.Label(log_frame, text="EVENT LOG",
                 font=("Consolas", 12, "bold"),
                 fg="#fefefe", bg=self.UI_BG).pack(anchor="w")
        self.event_log = tk.Text(log_frame, height=5, bg="#11212c",
                                 fg="#00ffa0", font=("Consolas", 10),
                                 state="disabled")
        self.event_log.pack(fill="x")

        # ===== LOWER PANEL (plots + gauges) ===============================
        lower = tk.Frame(self, bg=self.UI_BG)
        lower.grid(row=3, column=0, columnspan=2, sticky="ew", padx=80, pady=(0, 10))
        lower.columnconfigure(0, weight=2); lower.columnconfigure(1, weight=1)

        # -- strip-charts (2x2) --
        plot_frame = tk.Frame(lower, bg=self.UI_BG); plot_frame.grid(row=0, column=0, sticky="nsew")
        self.plot_fields = ["Alt", "Yaw", "Pitch", "Roll"]
        self.axes, self.lines, self.canvases = [], [], []

        for idx, field in enumerate(self.plot_fields):
            fig, ax = plt.subplots(figsize=(2.7, 1.5))
            fig.patch.set_facecolor(self.UI_BG)
            ax.set_facecolor(self.PLOT_BG)
            ax.set_title(f"{field} vs Time", color=self.FG_TXT, fontsize=9)
            ax.set_xlabel("t (s)", color=self.FG_TXT, fontsize=8)
            ax.set_ylabel(field, color=self.FG_TXT, fontsize=8)
            ax.tick_params(colors=self.FG_TXT, labelsize=8)
            line, = ax.plot([], [], linewidth=1.4, color=self.FG_ACCENT)

            r, c = divmod(idx, 2)
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.get_tk_widget().grid(row=r, column=c, padx=8, pady=2)

            self.axes.append(ax); self.lines.append(line); self.canvases.append(canvas)

        # -- analog gauges --
        gauge_frame = tk.Frame(lower, bg=self.UI_BG); gauge_frame.grid(row=0, column=1, sticky="n", padx=(30, 0))
        self.yaw_gauge   = AnalogGauge(gauge_frame, min_val=0,   max_val=360, unit="Yaw",   size=self.GAUGE_SIZE)
        self.pitch_gauge = AnalogGauge(gauge_frame, min_val=-90, max_val=90,  unit="Pitch", size=self.GAUGE_SIZE)
        self.roll_gauge  = AnalogGauge(gauge_frame, min_val=-180,max_val=180, unit="Roll",  size=self.GAUGE_SIZE)
        for g in (self.yaw_gauge, self.pitch_gauge, self.roll_gauge):
            g.pack(side="left", padx=6)

        # ===== start periodic updates =====================================
        self.update_clock()
        self.after(500, self._update_loop)

    # ───────────────────────────────────────────────────────────────────
    def update_clock(self):
        self.utc_label.config(text=f"UTC: {datetime.utcnow():%Y-%m-%d %H:%M:%S}")
        self.lst_label.config(text=f"LST: {datetime.now():%Y-%m-%d %H:%M:%S}")
        self.after(1000, self.update_clock)

    # ───────────────────────────────────────────────────────────────────
    def _update_loop(self):
        """Fetch the latest telemetry packet and refresh all widgets."""
        packet = self.telemetry.latest
        if packet is None:                    # no data yet
            self.after(200, self._update_loop)
            return

        # ----- gauges / numeric labels ---------------------------------
        self.yaw_gauge.set_value(packet["Yaw"])
        self.pitch_gauge.set_value(packet["Pitch"])
        self.roll_gauge.set_value(packet["Roll"])

        for key in ("Yaw", "Pitch", "Roll", "Alt"):
            self.labels[key].config(text=f"{packet[key]:.2f}")

        # ----- event log ----------------------------------------------
        self.event_log.config(state="normal")
        self.event_log.delete("1.0", "end")
        self.event_log.insert("end",
                              "\n".join(self.telemetry.event_log[-6:]) or "—")
        self.event_log.config(state="disabled")

        # ----- map + trajectory path ----------------------------------
        lat, lon = packet["Lat"], packet["Lon"]
        if lat and lon:
            self.map_marker.set_position(lat, lon)
            self.map_widget.set_position(lat, lon)
            self.trajectory_coords.append((lat, lon))
            if len(self.trajectory_coords) > 1:
                self.map_widget.set_path(self.trajectory_coords, color="blue")

        # ----- strip-charts -------------------------------------------
        t_arr = np.asarray(self.telemetry.data["time"])
        if t_arr.size >= 3:
            for ax, line, field in zip(self.axes, self.lines, self.plot_fields):
                y = np.asarray(self.telemetry.data[field])
                line.set_data(t_arr, y)
                ax.relim(); ax.autoscale_view()
        for c in self.canvases:
            c.draw_idle()

        # ----- demo health indicator ----------------------------------
        if uniform(0, 1) < 0.01:
            self.sys_health.config(text="SYSTEM: FAULT", fg="#ff5555")
            self.telemetry.add_event("SYSTEM FAULT: Watchdog triggered")
        else:
            self.sys_health.config(text="SYSTEM: OK", fg="#00ff6b")

        # schedule next update
        self.after(500, self._update_loop)
