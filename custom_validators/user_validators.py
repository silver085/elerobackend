from validator import validate


def validate_user_create(user):
    rules = {
        "username": "required",
        "password": "required",
        "repeat_password": "required",
        "email": "required|mail"
    }
    result = False
    errors = {}
    result, _, errors = validate({"username": user.username, "password": user.password, "repeat_password" : user.repeat_password, "email": user.email}, rules, return_info=True)
    if user.password != user.repeat_password:
        errors["password"] = {"password": "the passwords must match!"}

    return result, errors
