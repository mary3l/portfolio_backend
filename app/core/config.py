"""Application settings, read from the environment once at startup."""

import base64
import binascii
import json
from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated configuration. Missing or malformed values stop the app from
    booting, which is safer than discovering the problem on the first request."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = "Mabano Portfolio API"
    debug: bool = False

    supabase_url: str
    # Must be the service_role key: the anon key cannot write past RLS.
    supabase_key: SecretStr

    # Only this account may create/update/delete projects. Required on purpose —
    # an unset value would silently let every signed-in Supabase user write.
    admin_email: str

    # Comma-separated list, e.g. "http://localhost:3000,https://mabano.dev".
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # --- Contact form email (Resend) ---
    # Leave RESEND_API_KEY empty to disable the contact endpoint entirely; it
    # then returns 503 rather than silently dropping enquiries.
    resend_api_key: SecretStr | None = None
    # Where enquiries are delivered. Defaults to the admin account.
    contact_to_email: str = ""
    # Must be a verified sender. Resend's shared test domain works out of the box.
    contact_from_email: str = "Portfolio <onboarding@resend.dev>"

    @field_validator("supabase_url")
    @classmethod
    def _validate_supabase_url(cls, value: str) -> str:
        url = value.strip().rstrip("/")
        if not url.startswith("https://"):
            raise ValueError("SUPABASE_URL must start with https://")
        return url

    @field_validator("admin_email")
    @classmethod
    def _validate_admin_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email:
            raise ValueError("ADMIN_EMAIL must be an email address")
        return email

    @property
    def allowed_origins(self) -> list[str]:
        """CORS origins as a list, ignoring blanks and stray whitespace."""
        origins = (origin.strip() for origin in self.cors_origins.split(","))
        return [origin for origin in origins if origin]

    @property
    def contact_enabled(self) -> bool:
        """Whether the contact endpoint can actually deliver mail."""
        return self.resend_api_key is not None and bool(
            self.resend_api_key.get_secret_value().strip()
        )

    @property
    def contact_recipient(self) -> str:
        """Who receives enquiries — falls back to the admin account."""
        return self.contact_to_email.strip() or self.admin_email

    @property
    def supabase_key_role(self) -> str:
        """Best-effort role carried by SUPABASE_KEY, for the startup check.

        Supports both key formats: the new `sb_secret_` / `sb_publishable_`
        prefixes and the legacy JWTs with a `role` claim. Returns "unknown"
        rather than raising — this is a diagnostic, not validation.
        """
        key = self.supabase_key.get_secret_value()

        if key.startswith("sb_secret_"):
            return "service_role"
        if key.startswith("sb_publishable_"):
            return "anon"

        parts = key.split(".")
        if len(parts) != 3:
            return "unknown"
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        try:
            claims = json.loads(base64.urlsafe_b64decode(payload))
        except (ValueError, binascii.Error):
            return "unknown"
        role = claims.get("role")
        return role if isinstance(role, str) else "unknown"

    @property
    def can_write_to_supabase(self) -> bool:
        """Whether SUPABASE_KEY bypasses row level security.

        A read-only key still serves the public site fine, so this is a warning
        rather than a startup failure — but every create/update/delete will be
        rejected by Postgres with a row-level security error.
        """
        return self.supabase_key_role not in {"anon", "authenticated"}


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so the environment is parsed once per process.

    Injectable as a FastAPI dependency, and overridable in tests via
    `app.dependency_overrides[get_settings]`.
    """
    return Settings()  # type: ignore[call-arg]  # values come from the environment
