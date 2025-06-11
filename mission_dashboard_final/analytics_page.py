import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import time

class AnalyticsPage(tk.Frame):
    def __init__(self, master, telemetry, user, **kwargs):
        super().__init__(master, bg="#161f26", **kwargs)
        self.telemetry = telemetry
        self.user = user

        logo_frame = tk.Frame(self, bg="#161f26")
        logo_frame.pack(fill="x", pady=(8,2))
        try:
            logo_img = Image.open("AB_logo.png").resize((210, 48), Image.Resampling.LANCZOS)
            logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_frame, image=logo_tk, bg="#161f26")
            logo_label.image = logo_tk
        except:
            logo_label = tk.Label(logo_frame, text="AB ROCKETRY", font=("Consolas", 22, "bold"), fg="white", bg="#161f26")
        logo_label.pack(side="top")

        self.start_time = time.time()
        self.time_label = tk.Label(self, text="", font=("Consolas", 16, "bold"), fg="#00ffea", bg="#161f26")
        self.time_label.pack(pady=4)

        card = tk.Frame(self, bg="#101d29", bd=3, relief="groove")
        card.pack(padx=20, pady=22, fill="x")
        tk.Label(card, text="Mission Analytics", font=("Consolas", 22, "bold"), fg="#00eeff", bg="#101d29").pack(pady=12)
        self.stats_text = tk.Text(card, height=10, width=85, bg="#17232f", fg="#bbffee", font=("Consolas", 15))
        self.stats_text.pack(pady=8, padx=8)
        tk.Button(self, text="Download Analytics", font=("Consolas", 14, "bold"), bg="#131e2a", fg="#00ffea", command=self.save_analytics).pack(pady=14)
        self.after(1200, self.update_analytics)

    def update_analytics(self):
        d = self.telemetry.data
        t = np.array(d["time"])
        alt = np.array(d["Alt"])
        p = np.array(d["P"])
        temp = np.array(d["T"])
        accel = np.array(d["Accel"])
        gyro = np.array(d["Gyro"])
        stats = []
        if len(alt) > 3:
            stats.append(f"Altitude: min={alt.min():.2f}, max={alt.max():.2f}, avg={alt.mean():.2f}, avg(10s)={np.mean(alt[-20:]):.2f}")
        if len(p) > 3:
            stats.append(f"Pressure: min={p.min():.2f}, max={p.max():.2f}, avg={p.mean():.2f}, avg(10s)={np.mean(p[-20:]):.2f}")
        if len(temp) > 3:
            stats.append(f"Temp: min={temp.min():.2f}, max={temp.max():.2f}, avg={temp.mean():.2f}, avg(10s)={np.mean(temp[-20:]):.2f}")
        if len(accel) > 3:
            stats.append(f"Accel: min={accel.min():.2f}, max={accel.max():.2f}, avg={accel.mean():.2f}, avg(10s)={np.mean(accel[-20:]):.2f}")
        if len(gyro) > 3:
            stats.append(f"Gyro: min={gyro.min():.2f}, max={gyro.max():.2f}, avg={gyro.mean():.2f}, avg(10s)={np.mean(gyro[-20:]):.2f}")
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, "\n".join(stats) + "\n")
        self.stats_text.insert(tk.END, "Total Samples: {}\n".format(len(t)))
        # Mission time
        elapsed = int(time.time() - self.start_time)
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        self.time_label.config(text=f"Mission Elapsed Time: {h:02d}:{m:02d}:{s:02d}")
        self.after(1200, self.update_analytics)

    def save_analytics(self):
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            with open(filename, "w") as f:
                f.write(self.stats_text.get("1.0", tk.END))
