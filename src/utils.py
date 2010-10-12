from datetime import date

def next_birthday(birth):
    if birth:
        today = date.today()
        year = date.today().year
        this_year_birthday = date(year, birth.month, birth.day)
        if today > this_year_birthday:
            return date(year + 1, birth.month, birth.day)
        else:
            return this_year_birthday

def days_to_birthday(birth):
    if birth:
        td = next_birthday(birth) - date.today()
        return td.days
