import mysql.connector
import pyotp
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime, timedelta

# Database Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "secure_file_storage"

# Email Configuration (Update with your email credentials)
EMAIL_SENDER = "ishantrokka.10@gmail.com"
EMAIL_PASSWORD = "ESHANT1234"

def generate_otp():
    """Generates a 6-digit OTP using pyotp."""
    return pyotp.TOTP(pyotp.random_base32()).now()

def send_email_otp(receiver_email, otp):
    """Sends the OTP to the user's email."""
    try:
        msg = EmailMessage()
        msg.set_content(f"Your OTP for login: {otp}\nThis OTP is valid for 5 minutes.")

        msg["Subject"] = "Secure File Storage - OTP Verification"
        msg["From"] = EMAIL_SENDER
        msg["To"] = receiver_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print("✅ OTP sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def store_otp(email, otp):
    """Stores the OTP in the database with a validity period."""
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()

    expiry_time = datetime.now() + timedelta(minutes=5)  # OTP valid for 5 minutes
    cursor.execute("UPDATE users SET otp_code = %s, otp_valid_until = %s WHERE email = %s", (otp, expiry_time, email))

    conn.commit()
    cursor.close()
    conn.close()

def request_otp(email):
    """Generates an OTP and sends it to the user."""
    otp = generate_otp()
    if send_email_otp(email, otp):
        store_otp(email, otp)
        return True
    return False

if __name__ == "__main__":
    user_email = input("Enter your email: ")
    request_otp(user_email)
