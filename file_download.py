import os
import mysql.connector
import tkinter as tk
from tkinter import messagebox, filedialog

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="secure_file_storage"
    )

# Fetch files for user (excluding hidden files by default)
def fetch_files(email, include_hidden=False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, filename, file_path, hidden 
            FROM files 
            WHERE user_id = (SELECT id FROM users WHERE email = %s)
        """
        if not include_hidden:
            query += " AND hidden = 0"  # Exclude hidden files by default
        cursor.execute(query, (email,))
        files = cursor.fetchall()
        conn.close()
        return files
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error retrieving files: {err}")
        return []

# Download the selected file
def download_file(email):
    files = fetch_files(email)
    if not files:
        messagebox.showinfo("Info", "No files available for download.")
        return

    selection_win = tk.Toplevel()
    selection_win.title("Select a File to Download")

    file_var = tk.StringVar(value=files[0][1])  # Default to first file
    selected_file_id = tk.IntVar(value=files[0][0])  # Store the selected file ID

    file_frame = tk.Frame(selection_win)
    file_frame.pack(pady=10)

    def refresh_file_list(include_hidden=False):
        # Clear the current file list
        for widget in file_frame.winfo_children():
            widget.destroy()

        # Fetch files (including hidden if requested)
        files = fetch_files(email, include_hidden)

        # Repopulate the file list
        for file_id, filename, file_path, hidden in files:
            tk.Radiobutton(
                file_frame, 
                text=filename, 
                variable=file_var, 
                value=filename,
                command=lambda fid=file_id, fname=filename: [selected_file_id.set(fid), file_var.set(fname)]  # Update both selected_file_id and file_var
            ).pack(anchor="w")

    refresh_file_list()  # Initial file list (excluding hidden files)

    def confirm_download():
        selected_file = file_var.get()
        for file_id, filename, file_path, hidden in files:
            if filename == selected_file:
                destination = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=filename.replace(".enc", ""))
                if destination:
                    os.rename(file_path, destination)  # Move file
                    messagebox.showinfo("Success", "File downloaded successfully!")
                break

    def delete_file():
        file_id = selected_file_id.get()
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this file?")
        if confirm:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM files WHERE id = %s", (file_id,))
                file_path = cursor.fetchone()[0]
                cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
                conn.commit()
                conn.close()
                os.remove(file_path)  # Delete file from filesystem
                messagebox.showinfo("Success", "File deleted successfully!")
                selection_win.destroy()  # Close the selection window
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting file: {e}")

    def hide_file():
        file_id = selected_file_id.get()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE files SET hidden = 1 WHERE id = %s", (file_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "File hidden successfully!")
            refresh_file_list()  # Refresh the file list after hiding
        except Exception as e:
            messagebox.showerror("Error", f"Error hiding file: {e}")

    def open_hidden_files_window():
        hidden_files_win = tk.Toplevel()
        hidden_files_win.title("Manage Hidden Files")

        hidden_files = fetch_files(email, include_hidden=True)  # Fetch all files (including hidden)
        hidden_files = [file for file in hidden_files if file[3] == 1]  # Filter only hidden files

        if not hidden_files:
            messagebox.showinfo("Info", "No hidden files found.")
            hidden_files_win.destroy()
            return

        hidden_file_var = tk.StringVar(value=hidden_files[0][1])  # Default to first hidden file
        selected_hidden_file_id = tk.IntVar(value=hidden_files[0][0])  # Store the selected hidden file ID

        hidden_file_frame = tk.Frame(hidden_files_win)
        hidden_file_frame.pack(pady=10)

        for file_id, filename, file_path, hidden in hidden_files:
            tk.Radiobutton(
                hidden_file_frame, 
                text=filename, 
                variable=hidden_file_var, 
                value=filename,
                command=lambda fid=file_id, fname=filename: [selected_hidden_file_id.set(fid), hidden_file_var.set(fname)]  # Update selected_hidden_file_id and hidden_file_var
            ).pack(anchor="w")

        def unhide_file():
            file_id = selected_hidden_file_id.get()
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE files SET hidden = 0 WHERE id = %s", (file_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "File unhidden successfully!")
                hidden_files_win.destroy()  # Close the hidden files window
                refresh_file_list()  # Refresh the main file list
            except Exception as e:
                messagebox.showerror("Error", f"Error unhiding file: {e}")

        unhide_button = tk.Button(hidden_files_win, text="Unhide File", command=unhide_file)
        unhide_button.pack(pady=10)

    # Buttons for Download, Delete, Hide, and Manage Hidden Files
    button_frame = tk.Frame(selection_win)
    button_frame.pack(pady=10)

    download_button = tk.Button(button_frame, text="Download File", command=confirm_download)
    download_button.grid(row=0, column=0, padx=5, pady=5)

    delete_button = tk.Button(button_frame, text="Delete File", command=delete_file)
    delete_button.grid(row=0, column=1, padx=5, pady=5)

    hide_button = tk.Button(button_frame, text="Hide File", command=hide_file)
    hide_button.grid(row=0, column=2, padx=5, pady=5)

    manage_hidden_button = tk.Button(button_frame, text="Manage Hidden Files", command=open_hidden_files_window)
    manage_hidden_button.grid(row=0, column=3, padx=5, pady=5)

    selection_win.mainloop()