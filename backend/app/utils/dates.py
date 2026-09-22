from datetime import date, datetime


def parse_date(value):
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("日期格式应为 YYYY-MM-DD")


def parse_optional_date(value):
    if value in (None, ""):
        return None
    return parse_date(value)


def parse_month(value):
    if isinstance(value, date):
        return value.replace(day=1)
    if not value:
        return None
    try:
        parsed = datetime.strptime(str(value), "%Y-%m")
    except ValueError:
        raise ValueError("月份格式应为 YYYY-MM")
    return parsed.date().replace(day=1)


def add_months(value, months):
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    return date(year, month, 1)

