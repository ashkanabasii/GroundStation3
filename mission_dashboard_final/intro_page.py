import tkinter as tk

def show_intro_popup():
    doc_text = (
        "MISSION-READY TELEMETRY GROUND STATION SOFTWARE\n"
        "----------------------------------------------------------\n\n"
        "This software is designed for operational robustness and mission success in high-power rocketry, aerospace, and advanced research. "
        "It delivers a comprehensive real-time telemetry solution for professional or military field use, including:\n"
        "- Live sensor data monitoring (attitude, environment, health, GPS)\n"
        "- Secure operator login with call sign\n"
        "- Military-grade dashboard and analytics pages\n"
        "- GPS mapping with trajectory and export\n"
        "- Advanced analytics, event logging, and data export\n\n"
        "Developed for field reliability, expandability, and modern mission requirements. "
        "For inquiries or customization, contact: arbalest@rocketry-missions.com\n"
        "\n"
        "Version: 2.0 | For professional, aerospace, or defense use."
    )
    popup = tk.Toplevel()
    popup.title("About: Arbalest Rocketry Telemetry")
    popup.geometry("660x480")
    popup.configure(bg="#131c28")
    tk.Label(popup, text="Mission Documentation", font=("Consolas", 20, "bold"), fg="#00f0ff", bg="#131c28").pack(pady=22)
    txt = tk.Text(popup, wrap="word", font=("Consolas", 13), bg="#181f26", fg="#ddffee", height=16)
    txt.pack(fill="both", expand=True, padx=18)
    txt.insert(tk.END, doc_text)
    txt.configure(state="disabled")
    tk.Button(popup, text="Close", font=("Consolas", 13, "bold"), command=popup.destroy, bg="#223344", fg="#00f0ff").pack(pady=18)