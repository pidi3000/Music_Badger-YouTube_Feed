
from re import match
from datetime import datetime


def get_int_or_none(number: str) -> int | None:
    return int(number) if number and match(
        r'^-?[0-9]+$', number) else None


def get_time_group(time: datetime) -> str:
    time_groups = {
        "today": "Today",
        "yesterday": "Yesterday",

        "week": "This Week",
        "last_week": "Last Week",

        "month": "This Month",
        "last_month": "Last Month",

        "year": "This Year",
        "last_year": "Last Year",

        "older": "Long Ago",
    }

    time_now = datetime.now()
    time_elapsed = time_now - time

    # Day
    hours_ago = time_elapsed.total_seconds()/60/60
    if hours_ago <= 24:
        return time_groups["today"]

    if hours_ago <= 48:
        return time_groups["yesterday"]

    # Week
    days_ago = time_elapsed.total_seconds()/60/60/24
    if days_ago <= 7:
        return time_groups["week"]

    if days_ago <= 14:
        return time_groups["last_week"]

    # Month
    if days_ago <= 30:
        return time_groups["month"]

    if days_ago <= 60:
        return time_groups["last_month"]

    # Year
    if days_ago <= 365:
        return time_groups["year"]

    # Older
    return time_groups["older"]


def get_relative_time(time: datetime) -> str:
    time_now = datetime.now()

    # test_time = "2023-07-09T03:00:00"
    # time_now = datetime.strptime(test_time, YT_DATE_FORMAT)

    time_elapsed = time_now - time

    # print(time_elapsed)
    # print(time_elapsed.seconds)
    # print(time_elapsed.total_seconds())
    # print(time_elapsed.total_seconds() - (time_elapsed.days*24*60*60))
    # print(time_elapsed.days)

    # n seconds ago < 60
    time_section = time_elapsed.total_seconds()
    if time_section < 60:
        return "{} Seconds ago".format(int(time_section))

    # n Minutes ago < 60
    time_section = time_elapsed.total_seconds()/60
    if time_section < 60:
        return "{} Minutes ago".format(int(time_section))

    # n hours ago < 24
    time_section = time_elapsed.total_seconds()/60/60
    if time_section < 24:
        return "{} Hours ago".format(round(time_section, 1))

    # n days ago < 14
    time_section = time_elapsed.total_seconds()/60/60/24
    if time_section < 14:
        return "{} Days ago".format(round(time_section, 1))

    # n weeks ago < 4
    time_section = time_elapsed.total_seconds()/60/60/24/7
    if time_section < 4:
        return "{} Weeks ago".format(round(time_section, 1))

    # n months ago < 12     1 month = 30 days
    time_section = time_elapsed.total_seconds()/60/60/24/30
    if time_section < 12:
        return "{} Months ago".format(round(time_section, 1))

    # n years ago
    time_section = time_elapsed.total_seconds()/60/60/24/365
    return "{} Years ago".format(round(time_section, 1))
