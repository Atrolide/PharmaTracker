"""Package for AWS helper methods"""

import hmac
import hashlib
import base64


def calculate_secret_hash(client_id, client_secret, username):
    """Calculates SECRET_HASH parameter used for user registration"""
    message = username + client_id
    dig = hmac.new(
        str(client_secret).encode("utf-8"),
        msg=str(message).encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    secret_hash = base64.b64encode(dig).decode()
    return secret_hash
