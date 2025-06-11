import tkinter as tk

class LoginPage(tk.Frame):
    def __init__(self, master, on_login, **kwargs):
        super().__init__(master, bg="#171e24", **kwargs)
        self.on_login = on_login
        tk.Label(self, text="MISSION ACCESS", font=("Consolas", 28, "bold"), fg="#00f0ff", bg="#171e24").pack(pady=30)
        self.name_var = tk.StringVar()
        self.callsign_var = tk.StringVar()
        tk.Label(self, text="Name:", font=("Consolas", 17, "bold"), bg="#171e24", fg="#77eeff").pack(pady=5)
        tk.Entry(self, textvariable=self.name_var, font=("Consolas", 17), width=22).pack(pady=3)
        tk.Label(self, text="Call Sign:", font=("Consolas", 17, "bold"), bg="#171e24", fg="#77eeff").pack(pady=5)
        tk.Entry(self, textvariable=self.callsign_var, font=("Consolas", 17), width=22).pack(pady=3)
        tk.Button(self, text="LOG IN", font=("Consolas", 17, "bold"), width=18, bg="#131e2a", fg="#00ffea",
                  command=self.try_login).pack(pady=22)
    def try_login(self):
        n, c = self.name_var.get().strip(), self.callsign_var.get().strip()
        if n and c:
            self.on_login(n, c)