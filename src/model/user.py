class User:
    """Shared user data across all files and subclasses."""

    # Class variables (shared)
    id: int = None
    first_name: str = None
    last_name: str = None
    email_address: str = None
    avatar_url: str = None

    @classmethod
    def to_dict(cls) -> dict:
        """Return all shared user fields as a dict."""
        return {
            "id": cls.id,
            "first_name": cls.first_name,
            "last_name": cls.last_name,
            "email_address": cls.email_address,
            "avatar_url": cls.avatar_url,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Set shared user fields from a dict."""
        cls.id = data.get("id")
        cls.first_name = data.get("first_name")
        cls.last_name = data.get("last_name")
        cls.email_address = data.get("email_address")
        cls.avatar_url = data.get("avatar_url")

    @classmethod
    def set_field(cls, field: str, value):
        """Set a single shared field dynamically."""
        if hasattr(cls, field):
            setattr(cls, field, value)

    @classmethod
    def get_field(cls, field: str):
        """Get a single shared field dynamically."""
        return getattr(cls, field, None)