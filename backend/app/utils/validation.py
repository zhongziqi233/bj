import re


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def validate_username(username):
    if not username or len(username.strip()) < 3 or len(username.strip()) > 50:
        return "用户名长度需为 3-50 个字符"
    if re.search(r"\s", username):
        return "用户名不能包含空格"
    return None


def validate_email(email):
    if not email or len(email.strip()) > 120 or not EMAIL_RE.match(email.strip()):
        return "邮箱格式不正确"
    return None


def validate_password(password):
    if not password or len(password) < 8:
        return "密码长度至少为 8 位"
    if len(password) > 128:
        return "密码长度不能超过 128 位"
    return None

