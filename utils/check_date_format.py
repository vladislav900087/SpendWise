from datetime import datetime

def check_date_format(date_string: str) -> bool:
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

print(check_date_format('2020-01-10'))
print(check_date_format('10-20-2020'))