import uuid


def create_session_token():
    return uuid.uuid4().hex
