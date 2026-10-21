
import os
import getpass
from dotenv import load_dotenv
from supabase import create_client

# 1. Load .env
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase settings in .env")

# 2. Create Supabase client
supabase = create_client(supabase_url, supabase_key)

# 3. Ask for login credentials
email = input("Email: ")
password = getpass.getpass("Password: ")

# 4. Sign in
try:
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if response.user and response.session:
        print("Login successful!")
        print("User ID:", response.user.id)
        print("Email:", response.user.email)
    else:
        print("Login failed: No active session")

except Exception as e:
    print("Login failed:", e)
