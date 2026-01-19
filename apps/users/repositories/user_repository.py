from apps.users.models import User


def create_user(username: str, email: str, password: str) -> User:
    return User.objects.create_user(username=username, email=email, password=password)


def update_user(user: User, **fields) -> User:
    for field, value in fields.items():
        setattr(user, field, value)
    user.save(update_fields=list(fields.keys()))
    return user


def update_user_by_id(user_id: int, **fields) -> int:
    return User.objects.filter(id=user_id).update(**fields)
