def simpconvert_to_str(val):
    try:
        return str(val)
    except UnicodeEncodeError:
        return e.text.encode('ascii', 'ignore')
