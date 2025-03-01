import tkinter as tk
from tkinter import messagebox
import mysql.connector
import pyotp
import database_setup as db  # Import database setup
import register_window  # Import the register window script
import file_upload  # Ensure this is imported
import file_download

otp_storage = {}

# Function to generate OTP
def generate_otp():
    otp = pyotp.random_base32()
    return pyotp.TOTP(otp).now()

# Store OTP temporarily
def store_otp(email, otp):
    otp_storage[email] = otp
    print(f"OTP for {email}: {otp}")  # Debugging: Display OTP in console

# Verify OTP and log in
def verify_otp(email, entered_otp, login_win):
    if email in otp_storage and otp_storage[email] == entered_otp:
        messagebox.showinfo("Success", "✅ OTP Verified! Login Successful.")
        login_win.destroy()
        open_dashboard(email)  # Redirect to dashboard
    else:
        messagebox.showerror("Error", "❌ Incorrect OTP. Try again.")

# Request OTP for login
def request_otp(email):
    conn = mysql.connector.connect(host=db.DB_HOST, user=db.DB_USER, password=db.DB_PASSWORD, database=db.DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("Error", "❌ User not found! Please register first.")
    else:
        otp = generate_otp()
        store_otp(email, otp)
        messagebox.showinfo("OTP Sent", "✅ OTP has been generated. Enter it below.")

    cursor.close()
    conn.close()

# Open Dashboard after Login
def open_dashboard(email):
    """Opens the user dashboard after login."""
    dashboard_win = tk.Tk()
    dashboard_win.title("User Dashboard")
    dashboard_win.geometry("400x300")

    # Welcome Label
    tk.Label(dashboard_win, text=f"Welcome, {email}!", font=("Arial", 14)).pack(pady=10)

    # Force UI update
    dashboard_win.update_idletasks()  

    # Frame for Buttons (Ensures Alignment)
    button_frame = tk.Frame(dashboard_win)
    button_frame.pack(pady=10)

    # Upload File Button
    upload_button = tk.Button(button_frame, text="📤 Upload File", width=20, height=2, 
                              command=lambda: file_upload.upload_file(email))
    upload_button.grid(row=0, column=0, padx=10, pady=5)

    # Download File Button
    download_button = tk.Button(button_frame, text="📥 Download File", width=20, height=2, 
                                command=lambda: file_download.download_file(email))
    download_button.grid(row=0, column=1, padx=10, pady=5)

    # Logout Button
    logout_button = tk.Button(dashboard_win, text="🚪 Logout", width=20, height=2, 
                              command=lambda: [dashboard_win.destroy(), open_login_window()])
    logout_button.pack(pady=20)

    # Force Tkinter to process and display all widgets
    dashboard_win.update()
    
    dashboard_win.mainloop()

# Open the Login Window
def open_login_window():
    root = tk.Tk()
    root.title("Login")
    root.geometry("400x300")

    tk.Label(root, text="Login", font=("Arial", 14)).pack(pady=10)

    # Email Entry
    tk.Label(root, text="Email:").pack()
    email_entry = tk.Entry(root, width=30)
    email_entry.pack(pady=5)

    # OTP Section
    tk.Label(root, text="Enter OTP:").pack()
    otp_entry = tk.Entry(root, width=30)
    otp_entry.pack(pady=5)

    # Buttons
    request_otp_button = tk.Button(root, text="Request OTP", command=lambda: request_otp(email_entry.get()))
    request_otp_button.pack(pady=5)

    login_button = tk.Button(root, text="Login", command=lambda: verify_otp(email_entry.get(), otp_entry.get(), root))
    login_button.pack(pady=10)

    # Register Button (Opens Register Page)
    register_button = tk.Button(root, text="Register", command=lambda: [root.destroy(), register_window.open_register_window()])
    register_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    open_login_window()
