from datetime import datetime, timedelta


def get_last_friday() -> datetime.date:
    today = datetime.today()
    days_back = (today.weekday() - 4) % 7
    if days_back == 0:
        days_back = 7
    last_friday = today - timedelta(days=days_back)
    return last_friday.strftime("%Y-%m-%d")


def parse_gross(value: str) -> int:
    if value == "-":
        return 0
    return int(value.replace("$", "").replace(",", ""))


def parse_date_range(date_range):
    # Split the date range into start and end
    parts = date_range.split(' ')
    start_month = parts[0]
    start_day = parts[1].split('-')[0]
    if '-' in parts[1]:
        if len(parts) == 4:
            end_month = parts[2]
            end_day = parts[1].split('-')[1]
        else:
            end_month = start_month
            end_day = parts[1].split('-')[1]
    else:
        end_month = parts[0]
        end_day = parts[1]

    # Extract the year
    year = parts[-1]

    # Create the start and end date strings
    start_date_str = f"{start_month} {start_day} {year}"
    end_date_str = f"{end_month} {end_day} {year}"

    # Parse the dates
    start_date = datetime.strptime(start_date_str, "%b %d %Y")
    try:
        end_date = datetime.strptime(end_date_str, "%b %d %Y")
    except ValueError:
        end_date = datetime.strptime(end_date_str, "%d %b %Y")

    return start_date, end_date
