from schemas.user import CurrentUser

def get_worker_from_token(decoded_token: dict,) -> CurrentUser:

    return CurrentUser(
        uid=decoded_token["uid"],
        email=decoded_token.get("email"),
    )