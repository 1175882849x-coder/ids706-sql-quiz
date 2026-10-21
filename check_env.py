
import os
from dotenv import load_dotenv

load_dotenv(override=True)

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()

print("URL format:", url.startswith("https://") and url.endswith(".supabase.co"))
print("Key format:", key.startswith("sb_publishable_"))
print("Key length:", len(key))
print("Key contains ellipsis:", "..." in key)
