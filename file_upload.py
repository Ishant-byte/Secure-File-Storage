import tkinter as tk
from tkinter import filedialog, messagebox
import os
import mysql.connector
import database_setup as db
from Crypto.Cipher import AES
import hashlib
import threading  # ✅ Multi-threading for non-blocking operations

SECRET_KEY = hashlib.sha256(b"super_secret_key").digest()  # 256-bit AES key

def encrypt_file(input_file, output_file):
    """Encrypts the file using AES-256 encryption."""
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    with open(input_file, "rb") as f:
        file_data = f.read()
    
    ciphertext, tag = cipher.encrypt_and_digest(file_data)
    
    with open(output_file, "wb") as f:
        f.write(cipher.nonce)  # Store nonce
        f.write(tag)
        f.write(ciphertext)

    print(f"✅ File encrypted: {output_file}")

def upload_file(email):
    """Handles file upload using a separate thread for encryption."""
    print(f"✅ Upload File button clicked for {email}")  

    file_path = filedialog.askopenfilename(title="Select a File")
    
    if not file_path:
        messagebox.showwarning("Warning", "⚠ No file selected. Please select a file to upload.")
        return

    file_name = os.path.basename(file_path)
    storage_folder = "encrypted_files"
    os.makedirs(storage_folder, exist_ok=True)  

    encrypted_path = os.path.join(storage_folder, file_name + ".enc")

    def threaded_upload():
        encrypt_file(file_path, encrypted_path)  # Run encryption in a separate thread

        try:
            conn = mysql.connector.connect(host=db.DB_HOST, user=db.DB_USER, password=db.DB_PASSWORD, database=db.DB_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_id = cursor.fetchone()

            if user_id:
                cursor.execute("INSERT INTO files (user_id, filename, file_path, encryption_method) VALUES (%s, %s, %s, %s)", 
                               (user_id[0], file_name + ".enc", encrypted_path, "AES-256"))
                conn.commit()
                messagebox.showinfo("Success", f"✅ File '{file_name}.enc' uploaded securely!")

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"❌ Error uploading file: {e}")

    # ✅ Run file encryption and database insertion in a separate thread
    threading.Thread(target=threaded_upload, daemon=True).start()
