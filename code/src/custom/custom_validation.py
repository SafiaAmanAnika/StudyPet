# Minimal manual validators to avoid regex dependency.


def is_valid_email(email):
    if email is None:
        return False

    email = str(email).strip().lower()
    if not email or "@" not in email:
        return False

    parts = email.split("@")
    if len(parts) != 2:
        return False

    local, domain = parts[0], parts[1]
    if not local or not domain:
        return False

    allowed_local = "abcdefghijklmnopqrstuvwxyz0123456789._%+-"
    allowed_domain = "abcdefghijklmnopqrstuvwxyz0123456789.-"

    if local[0] == "." or local[-1] == ".":
        return False
    if ".." in local:
        return False

    for ch in local:
        if ch not in allowed_local:
            return False

    if domain[0] in ".-" or domain[-1] in ".-":
        return False
    if ".." in domain:
        return False

    for ch in domain:
        if ch not in allowed_domain:
            return False

    labels = domain.split(".")
    if len(labels) < 2:
        return False
    for label in labels:
        if not label:
            return False
        if label[0] == "-" or label[-1] == "-":
            return False

    tld = labels[-1]
    if len(tld) < 2:
        return False
    for ch in tld:
        if not ("a" <= ch <= "z"):
            return False

    return True
