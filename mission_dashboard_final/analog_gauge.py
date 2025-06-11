import tkinter as tk
from math import sin, cos, radians

class AnalogGauge(tk.Canvas):
    def __init__(self, master=None, min_val=0, max_val=100, unit="Unit", size=150, **kwargs):
        super().__init__(master, width=size, height=size, bg="#11212c", highlightthickness=0, **kwargs)
        self.size = size
        self.center = size // 2
        self.radius = int(self.center * 0.8)
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.value = min_val
        self.needle = None
        self.text_unit = None
        self.value_text = None  # <-- No more value_box
        self.draw_gauge()
        self.set_value(self.value)

    def draw_gauge(self):
        # Background arc
        self.create_oval(self.center - self.radius, self.center - self.radius,
                         self.center + self.radius, self.center + self.radius,
                         outline="#00f0ff", width=4)

        # Ticks
        for angle in range(-135, 136, 45):
            x0 = self.center + (self.radius - 8) * cos(radians(angle))
            y0 = self.center + (self.radius - 8) * sin(radians(angle))
            x1 = self.center + self.radius * cos(radians(angle))
            y1 = self.center + self.radius * sin(radians(angle))
            self.create_line(x0, y0, x1, y1, fill="#ffffff", width=2)

        # Needle
        self.needle = self.create_line(self.center, self.center,
                                       self.center, self.center - self.radius + 16,
                                       fill="#00ff90", width=4)

        # Unit label (bottom)
        self.text_unit = self.create_text(self.center, self.center + self.radius // 1.5,
                                          text=self.unit, fill="#cccccc", font=("Consolas", 10, "bold"))

        # Value text only (no box)
        self.value_text = self.create_text(self.center, self.center + 25,
                                           text="0.0", fill="#00ffff", font=("Consolas", 11, "bold"))

    def set_value(self, val):
        val = max(self.min_val, min(self.max_val, val))
        self.value = val

        # Update needle position
        angle = -135 + 270 * (val - self.min_val) / (self.max_val - self.min_val)
        x = self.center + (self.radius - 16) * cos(radians(angle))
        y = self.center + (self.radius - 16) * sin(radians(angle))
        self.coords(self.needle, self.center, self.center, x, y)

        # Update value and unit
        self.itemconfigure(self.value_text, text=f"{val:.1f}")
        self.itemconfigure(self.text_unit, text=self.unit)

