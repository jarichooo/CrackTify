import re

def validate_registration(
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str
    ) -> tuple[bool, dict]:
    """
    Validates registration fields.
    Returns:
        is_valid (bool): True if all validations pass
        errors (dict): field-specific error messages
    """
    errors = {}
    is_valid = True

    # Validate first name
    if not first_name.strip():
        errors["first_name"] = "Please enter your first name."
        is_valid = False

    # Validate last name
    if not last_name.strip():
        errors["last_name"] = "Please enter your last name."
        is_valid = False

    # Validate email
    if not email.strip():
        errors["email"] = "Please enter your email."
        is_valid = False
    # Email format check
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = "Please enter a valid email address."
        is_valid = False

    # Validate password
    if not password:
        errors["password"] = "Please enter your password."
        is_valid = False
    else:
        if len(password) < 8:
            errors["password"] = "Password must be at least 8 characters long."
            is_valid = False

        elif not re.search(r"[a-z]", password):
            errors["password"] = "Password must contain at least one lowercase letter."
            is_valid = False

        elif not re.search(r"[A-Z]", password):
            errors["password"] = "Password must contain at least one uppercase letter."
            is_valid = False

        elif not re.search(r"[0-9]", password):
            errors["password"] = "Password must contain at least one number."
            is_valid = False

        elif not re.search(r"[^a-zA-Z0-9]", password):
            errors["password"] = "Password must contain at least one symbol."
            is_valid = False

    # Validate confirm password
    if not confirm_password:
        errors["confirm_password"] = "Please confirm your password."
        is_valid = False
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."
        is_valid = False

    return is_valid, errors

def validate_login(email: str, password: str) -> tuple[bool, dict]:
    """
    Validates login fields.
    Returns:
        is_valid (bool): True if all validations pass
        errors (dict): field-specific error messages
    """
    errors = {}
    is_valid = True

    # Validate email
    if not email.strip():
        errors["email"] = "Please enter your email."
        is_valid = False
    # Email format check
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = "Please enter a valid email address."
        is_valid = False

    # Validate password
    if not password:
        errors["password"] = "Please enter your password."
        is_valid = False

    return is_valid, errors