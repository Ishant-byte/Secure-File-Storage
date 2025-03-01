import tkinter as tk
from tkinter import messagebox
import mysql.connector
import database_setup as db  # Import database setup
import login_window  # Import login window to return after registering

# Register a new user
def register_user(username, email):
    if not username or not email:
        messagebox.showwarning("Warning", "Please enter both username and email.")
        return

    try:
        conn = mysql.connector.connect(host=db.DB_HOST, user=db.DB_USER, password=db.DB_PASSWORD, database=db.DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            messagebox.showerror("Error", "❌ User already exists! Please login instead.")
        else:
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                           (username, email, "default_hashed_password"))
            conn.commit()
            messagebox.showinfo("Success", "✅ Registration successful! Please login.")
            root.destroy()
            login_window.open_login_window()  # Redirect back to login

        cursor.close()
        conn.close()

    except mysql.connector.IntegrityError as err:
        messagebox.showerror("Database Error", f"❌ MySQL Integrity Error: {err}")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"❌ MySQL Error: {err}")

# Open the Register Window
def open_register_window():
    global root
    root = tk.Tk()
    root.title("Register")
    root.geometry("400x300")

    tk.Label(root, text="Register", font=("Arial", 14)).pack(pady=10)

    # Username Entry
    tk.Label(root, text="Username:").pack()
    username_entry = tk.Entry(root, width=30)
    username_entry.pack(pady=5)

    # Email Entry
    tk.Label(root, text="Email:").pack()
    email_entry = tk.Entry(root, width=30)
    email_entry.pack(pady=5)

    # Register Button
    register_button = tk.Button(root, text="Register", command=lambda: register_user(username_entry.get(), email_entry.get()))
    register_button.pack(pady=10)

    # Back to Login Button
    back_button = tk.Button(root, text="Back to Login", command=lambda: [root.destroy(), login_window.open_login_window()])
    back_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    open_register_window()
