import tkinter as tk
from tkinter import messagebox
import login_window

# Import modules correctly
try:
    import file_upload  # Ensure file_upload.py exists in the same directory
    import file_download  # Ensure file_download.py exists in the same directory
except ModuleNotFoundError:
    messagebox.showerror("Error", "❌ Missing file_upload.py or file_download.py!")

# Global variable to track Dark Mode state
dark_mode = False  

def toggle_theme(root, widgets):
    """Switch between Light and Dark Mode dynamically."""
    global dark_mode
    dark_mode = not dark_mode  # Toggle the mode

    bg_color = "black" if dark_mode else "white"
    fg_color = "white" if dark_mode else "black"
    btn_bg = "#444" if dark_mode else "#f0f0f0"  # Button background
    btn_fg = "white" if dark_mode else "black"

    root.configure(bg=bg_color)

    # Apply colors to all widgets
    for widget in widgets:
        try:
            widget.configure(bg=bg_color, fg=fg_color)
        except:
            pass  # Some widgets may not support fg/bg properties

    # Special handling for buttons
    for btn in widgets.get("buttons", []):
        btn.configure(bg=btn_bg, fg=btn_fg)

def open_dashboard(email):
    """Opens the user dashboard after login."""
    print("✅ Dashboard function called")  
    dashboard_win = tk.Tk()
    dashboard_win.title("User Dashboard")
    dashboard_win.geometry("400x300")

    # UI Elements
    label = tk.Label(dashboard_win, text=f"Welcome, {email}!", font=("Arial", 14))
    label.pack(pady=10)

    button_frame = tk.Frame(dashboard_win)
    button_frame.pack(pady=10)

    upload_button = tk.Button(button_frame, text="📤 Upload File", width=20, height=2, 
                              command=lambda: file_upload.upload_file(email))
    upload_button.grid(row=0, column=0, padx=10, pady=5)

    download_button = tk.Button(button_frame, text="📥 Download File", width=20, height=2, 
                                command=lambda: file_download.download_file(email))
    download_button.grid(row=0, column=1, padx=10, pady=5)


    # Logout Button
    logout_button = tk.Button(dashboard_win, text="🚪 Logout", width=20, height=2, 
                              command=lambda: [dashboard_win.destroy(), login_window.open_login_window()])
    logout_button.pack(pady=20)

    # Store widgets for theming
    widgets = {
        "labels": [label],
        "buttons": [upload_button, download_button, logout_button]
    }

    dashboard_win.mainloop()
