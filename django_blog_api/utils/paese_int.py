def try_parse_int(value):
    """
    Attempts to parse a value as an integer.
    Returns the integer value if successful, or None if parsing fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return None