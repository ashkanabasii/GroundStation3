import tkinter as tk
from PIL import Image, ImageTk
from tkintermapview import TkinterMapView

class GPSPage(tk.Frame):
    def __init__(self, master, telemetry, user, **kwargs):
        super().__init__(master, bg="#151e24", **kwargs)
        self.telemetry = telemetry
        self.user = user

        # Logo
        logo_frame = tk.Frame(self, bg="#151e24")
        logo_frame.pack(fill="x", pady=(8,2))
        try:
            logo_img = Image.open("AB_logo.png").resize((310, 70), Image.Resampling.LANCZOS)
            logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_frame, image=logo_tk, bg="#151e24")
            logo_label.image = logo_tk
        except:
            logo_label = tk.Label(logo_frame, text="AB ROCKETRY", font=("Consolas", 26, "bold"), fg="white", bg="#151e24")
        logo_label.pack(side="top", pady=2)

        # Centered map (fills width)
        map_frame = tk.Frame(self, bg="#151e24")
        map_frame.pack(fill="both", expand=True)
        self.map_widget = TkinterMapView(map_frame, width=1150, height=650, corner_radius=14)
        self.map_widget.pack(fill="both", expand=True, padx=18, pady=8)
        self.map_widget.set_position(43.7735, -79.5015)
        self.map_marker = self.map_widget.set_marker(43.7735, -79.5015, text="Rocket")
        self.trajectory_coords = []

        # Overlay info
        overlay = tk.Frame(self.map_widget, bg="#162026")
        overlay.place(relx=0.80, rely=0.03)
        self.lat_lbl = tk.Label(overlay, text="Lat: ---", font=("Consolas", 14), fg="#aaffdd", bg="#162026")
        self.lon_lbl = tk.Label(overlay, text="Lon: ---", font=("Consolas", 14), fg="#aaffdd", bg="#162026")
        self.lat_lbl.grid(row=0, column=0, padx=8, pady=3)
        self.lon_lbl.grid(row=1, column=0, padx=8, pady=3)
        tk.Button(overlay, text="Save Last Location", font=("Consolas", 11, "bold"), bg="#12222a", fg="#00eeff", command=self.save_location).grid(row=2, column=0, pady=6, sticky="ew")
        tk.Button(overlay, text="Export Map", font=("Consolas", 11, "bold"), bg="#12222a", fg="#00eeff", command=self.export_map).grid(row=3, column=0, pady=2, sticky="ew")
        self.after(1000, self.update_gps)

    def update_gps(self):
        d = self.telemetry.data
        if d["Lat"] and d["Lon"]:
            lat = d["Lat"][-1]
            lon = d["Lon"][-1]
            self.lat_lbl.config(text=f"Lat: {lat:.6f}")
            self.lon_lbl.config(text=f"Lon: {lon:.6f}")
            self.map_marker.set_position(lat, lon)
            self.map_widget.set_position(lat, lon)
            self.trajectory_coords.append((lat, lon))
            if len(self.trajectory_coords) > 1:
                self.map_widget.set_path(self.trajectory_coords, color="blue")
        self.after(1000, self.update_gps)

    def save_location(self):
        from tkinter import filedialog
        d = self.telemetry.data
        if d["Lat"] and d["Lon"]:
            filename = filedialog.asksaveasfilename(defaultextension=".txt")
            if filename:
                with open(filename, "w") as f:
                    f.write(f"Latitude: {d['Lat'][-1]:.6f}\nLongitude: {d['Lon'][-1]:.6f}\n")

    def export_map(self):
        from tkinter import messagebox
        messagebox.showinfo("Export Map", "Map image export is a placeholder in this prototype.")
