import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Optional: if set, only this Supabase account may create/update/delete projects.
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

_missing = [
    name
    for name, value in [
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_KEY", SUPABASE_KEY),
    ]
    if not value
]
if _missing:
    raise RuntimeError(
        f"Missing environment variables: {', '.join(_missing)} — check your .env file"
    )
