import pyotp
from datetime import datetime, timedelta

# Local OTP Storage (In-memory, for simplicity)
otp_storage = {}

def generate_otp():
    """Generates a 6-digit OTP using pyotp."""
    otp = pyotp.random_base32()  # Random OTP key
    return pyotp.TOTP(otp).now()

def store_otp(email, otp):
    """Stores the OTP and its expiration time in memory (local storage)."""
    expiry_time = datetime.now() + timedelta(seconds=20)  # OTP valid for 5 minutes
    otp_storage[email] = {'otp': otp, 'expiry': expiry_time}
    print(f"OTP stored for {email}. Expires at {expiry_time}")

def verify_otp(email, entered_otp):
    """Verifies if the OTP is correct and not expired."""
    if email not in otp_storage:
        print("❌ No OTP found for this email. Request a new OTP.")
        return False

    stored_otp = otp_storage[email]['otp']
    otp_valid_until = otp_storage[email]['expiry']

    if datetime.now() > otp_valid_until:
        print("❌ OTP expired! Request a new one.")
        del otp_storage[email]  # Remove expired OTP
        return False

    if entered_otp == stored_otp:
        print("✅ OTP Verified! Login Successful.")
        del otp_storage[email]  # OTP is consumed after successful login
        return True
    else:
        print("❌ Incorrect OTP. Please try again.")
        return False

if __name__ == "__main__":
    user_email = input("Enter your email: ")
    
    # Step 1: Generate and store OTP
    otp = generate_otp()
    store_otp(user_email, otp)
    
    # Step 2: Ask user to enter OTP
    entered_otp = input(f"Enter the OTP sent to {user_email}: ")
    
    # Step 3: Verify OTP
    verify_otp(user_email, entered_otp)
