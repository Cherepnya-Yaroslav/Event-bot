import datetime

def validate_date(date_text):
    try:
        date = datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return date >= datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        return False
