import datetime
import string
import re
from .functional import mapp, pipe, stapler

def route_num_to_letter(name):
    """
    Takes 'Route int'throws away 'Route' and 
    changes int to uppercase letter.
    """
    _, num = name.split()
    index = int(num) - 1
    return string.ascii_uppercase[index]

def apply_route_name_change(stop):
    return route_num_to_letter(stop['route_num'])

def change_keys(dictionary:dict) -> dict:
    return{key.lower().replace('#', 'num').replace(' ', '_'): dictionary[key] 
           for key in dictionary.keys()}

def string_box(stop:dict) -> str:
    """
    A hack...
    """
    return  stop['box_type'] + ' ' + stop['box_menu'] + ' ' + stop['box_size']

def extract_date_and_time(order):
    return order[0]['delivery_date'], order[0]['deliverytime']
    
def format_phone(phone_number):
    area_code, first, last = tuple(re.findall(r'\d{4}$|\d{3}', phone_number))
    return f'({area_code}) {first}-{last}'

def fix_phone(stop):
    phone_digits = re.findall('[0-9]{10}', stop['phone']) # attempts to find a coherent phone number.
    if phone_digits:
        stop['phone'] = format_phone(phone_digits[0])
    if len(phone_digits) > 1:
        stop['delivery_notes'] = stop['delivery_notes'] + f" Alternate phone: {format_phone(phone_digits[1])}"
    return stop

def try_parsing_date(text):
    for fmt in ('%B %d, %Y','%Y-%m-%d', '%m/%d/%Y', '%d-%b-%y'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

def clean_upload(order):
    return pipe(order,
        mapp(change_keys),
        lambda lst: list(filter(
            lambda stop: stop['route_num'] != 'DISMISSED REQUEST', lst)),
        mapp(fix_phone),
        mapp(stapler('box', string_box)),
        mapp(stapler('route_num', apply_route_name_change))
    )