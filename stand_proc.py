def simpconvert_to_str(val):
    try:
        return str(val)
    except UnicodeEncodeError:
        return e.text.encode('ascii', 'ignore')

class NFL_Schedule_Error(Exception):
    def __init__(self, message):
        self.message = message

