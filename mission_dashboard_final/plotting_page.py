import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PlottingPage(tk.Frame):
    def __init__(self, master, telemetry, user, **kwargs):
        super().__init__(master, bg="#181f26", **kwargs)
        self.telemetry = telemetry
        self.user = user

        # Logo row
        logo_frame = tk.Frame(self, bg="#181f26")
        logo_frame.pack(fill="x", pady=(8,2))
        try:
            logo_img = Image.open("AB_logo.png").resize((260, 58), Image.Resampling.LANCZOS)
            logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_frame, image=logo_tk, bg="#181f26")
            logo_label.image = logo_tk
        except:
            logo_label = tk.Label(logo_frame, text="AB ROCKETRY", font=("Consolas", 26, "bold"), fg="white", bg="#181f26")
        logo_label.pack(side="top")

        # Digital sensor values above plots
        vals_frame = tk.Frame(self, bg="#181f26")
        vals_frame.pack(pady=(8,2))
        self.vals = {k: tk.Label(vals_frame, text="---", font=("Consolas", 18, "bold"), fg="#77eeff", bg="#181f26", width=10)
            for k in ["Yaw","Pitch","Roll","Alt","P","T","Accel","Gyro"]}
        for k in self.vals:
            tk.Label(vals_frame, text=k, font=("Consolas", 13, "bold"), bg="#181f26", fg="#bbffee").pack(side="left", padx=(10,1))
            self.vals[k].pack(side="left", padx=(0,8))

        # 2x2 Grid of Plots
        plot_keys = ["Alt","P","Accel","Gyro","T","Lat","Lon"]
        self.axs, self.lines, self.canvases = [], [], []
        plot_frame = tk.Frame(self, bg="#181f26")
        plot_frame.pack(fill="both", expand=True, padx=18, pady=10)
        self.keys = plot_keys[:4]
        for i in range(2):
            for j in range(2):
                idx = 2 * i + j
                if idx >= len(self.keys): continue
                fig, ax = plt.subplots(figsize=(4.2,2.4))
                fig.patch.set_facecolor('#181f26')
                ax.set_facecolor('#131b22')
                ax.set_title(f"{self.keys[idx]} vs Time", color='#e0eefa', fontsize=12)
                ax.set_xlabel("Time (s)", color='#e0eefa', fontsize=10)
                ax.set_ylabel(self.keys[idx], color='#e0eefa', fontsize=10)
                line, = ax.plot([], [], color='#00ffea', linewidth=1.8)
                canvas = FigureCanvasTkAgg(fig, master=plot_frame)
                canvas.get_tk_widget().grid(row=i, column=j, padx=14, pady=8)
                self.axs.append(ax)
                self.lines.append(line)
                self.canvases.append(canvas)

        # Bottom controls
        btns_frame = tk.Frame(self, bg="#181f26")
        btns_frame.pack(side="bottom", pady=16)
        tk.Button(btns_frame, text="Export CSV", font=("Consolas", 11, "bold"), bg="#13212a", fg="#00ffea", command=self.export_csv).pack(side="left", padx=14)
        tk.Button(btns_frame, text="Capture Plot", font=("Consolas", 11, "bold"), bg="#13212a", fg="#00ffea", command=self.capture_plot).pack(side="left", padx=14)

        self.after(1000, self.update_page)

    def update_page(self):
        d = self.telemetry.data
        for k in self.vals:
            if d[k]:
                self.vals[k].config(text=f"{d[k][-1]:.2f}" if isinstance(d[k][-1], float) else d[k][-1])
        times = np.array(d["time"])
        for i, key in enumerate(self.keys):
            if key not in d or len(times) != len(d[key]) or len(times) < 2:
                continue
            y = np.array(d[key])
            self.lines[i].set_data(times, y)
            self.axs[i].relim()
            self.axs[i].autoscale_view()
            self.canvases[i].draw()
        self.after(1000, self.update_page)

    def export_csv(self):
        from tkinter import filedialog
        d = self.telemetry.data
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if filename:
            keys = list(d.keys())
            with open(filename, "w") as f:
                f.write(",".join(keys) + "\n")
                for i in range(len(d["time"])):
                    f.write(",".join([str(d[k][i]) if len(d[k]) > i else "" for k in keys]) + "\n")

    def capture_plot(self):
        from tkinter import filedialog
        for i, canvas in enumerate(self.canvases):
            filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")], title=f"Save Plot {i+1}")
            if filename:
                canvas.figure.savefig(filename)
