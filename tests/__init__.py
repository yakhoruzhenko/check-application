import datetime
import random
import string
import sys

from app.schemas.user import UserResponseWithChecks

sys.path.append('..')


class SeededUser(UserResponseWithChecks):
    password: str


def random_string(k: int = 10) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))

def datetime_to_str(dt: datetime.datetime) -> str:
    return dt.astimezone(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
