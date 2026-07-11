import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

_missing = [
    name
    for name, value in [
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_KEY", SUPABASE_KEY),
        ("ADMIN_API_KEY", ADMIN_API_KEY),
    ]
    if not value
]
if _missing:
    raise RuntimeError(
        f"Missing environment variables: {', '.join(_missing)} — check your .env file"
    )
