from typing import Hashable
import csv
import io

from shareplum import Site, Office365
from django.conf import settings
from collections import defaultdict


column_order = ['Delivery ID', 
                'Address', 
		'City', 
		'State', 
		'ZIP', 
		'Box Menu', 
		'Box Size', 
		'Box Type',
		'Call Status',  
		'DairyFree',
		'Delivery Date', 
		'Delivery Notes', 
		'Delivery Status', 
		'DeliveryDay',
		'DeliveryNumber', 
		'DeliveryTime', 
		'DeliveryZone', 
		'Driver Notes',
		'First Name',
		'Healthcare Partner', 
		'MainContact', 
		'Member ID', 
		'PeanutFree',
		'Phone', 
		'Primary Language',  
		'TextOptIn',]


def groupby(dictionaries: list, group_key: Hashable) -> dict:
    """
    Group a list of dictionaries by the values of a given key.
    """
    result = defaultdict(lambda: [])
    for dictionary in dictionaries:
        result[dictionary[group_key]].append(dictionary.copy())
    
    return dict(result)


def index(dictionaries: list, field: Hashable) -> dict:
    if len({item[field] for item in dictionaries}) != len(dictionaries):
        raise ValueError("Field must be unique for each dictionary.")
    return {dictionary[field] for dictionary in dictionaries}


def ungroup(dictionary: dict) -> list:
    """wrapper for  dict.values, but is opposite of groupby"""
    return [value for group in dictionary.values() for value in group]


def fill_in_missing_box(stop, box_info):
    for field in ['Box Type', 'Box Menu', 'Box Size']:
        stop[field] = box_info[field]
    return stop


def make_member_id_query(list_of_ids):
    query = {'Where':[]}
    for record in list_of_ids[:-1]:
        query['Where'].append('Or')
        query['Where'].append(('Eq', 'Member ID', record['Member ID']))

    query['Where'].append(('Eq', 'Member ID', 
                        list_of_ids[-1]['Member ID']))
    return query


def collect_time_span(starting: str, ending: str):
    # prepare the authcook and load the site
    authcookie = Office365('https://gcfbsm.sharepoint.com', 
                        settings.SP_USERNAME, 
                settings.SP_PASSWORD).GetCookies()
    site = Site('https://gcfbsm.sharepoint.com/sites/DMS', 
                authcookie=authcookie)

    query = {'Where':['And', ('Geq','Delivery Date', starting),
                  ('Leq','Delivery Date', ending),]}


    deliveries_list = site.List('Deliveries')

    return deliveries_list.get_list_items(query=query)


def collect_time_blocks(date):
    # prepare the authcook and load the site
    authcookie = Office365('https://gcfbsm.sharepoint.com', 
                        settings.SP_USERNAME, 
                settings.SP_PASSWORD).GetCookies()
    site = Site('https://gcfbsm.sharepoint.com/sites/DMS', 
                authcookie=authcookie)

    # create the query that collects future deliveries for selected date.
    query = {'Where': ['And', ('Eq', 'Delivery Date', date),
                            ('Eq', 'Delivery Status', 'Future')]}

    deliveries_list = site.List('Deliveries')

    deliveries = deliveries_list.get_list_items(query=query)

    # turn dates to strings
    for stop in deliveries:
        stop['Delivery Date'] = stop['Delivery Date'].strftime('%B %d, %Y')
        stop['Modified'] = stop['Modified'].strftime('%B %d, %Y')
    
    # find any deliveries that are missing box information and load 
    # the constituents list to see if it can be found there.
    need_box_types = [stop['Member ID'] for stop in deliveries 
                    if not (stop['Box Type']
                       and stop['Box Menu']
                       and stop['Box Size'])]

    if need_box_types:

        constituents_list = site.List('Constituents')

        query = make_member_id_query(need_box_types)

        box_infos = constituents_list.get_list_items(query=query, 
                                                fields=['Member ID', 
                                                        'BoxType', 
                                                        'Box Menu', 
                                                        'Box Size'])

        member_id_to_box_info = index(box_infos, 'Member ID')

        # fill in delivery with box type from constituents

        for stop in deliveries:
            if stop['Member ID'] in need_box_types:
                box_info = member_id_to_box_info[stop['Member ID']]
                fill_in_missing_box(stop, box_info)
    healthplan_groups = groupby(deliveries, 'Healthcare Partner')

    # split covenant off from rest of deliveries
    covenant = healthplan_groups.pop('Covenant', None)
    ungrouped = ungroup(healthplan_groups)
    time_groups = groupby(ungrouped, 'DeliveryTime')
    if covenant:
        time_groups['Covenant'] = covenant

    return time_groups


def make_csv(time_group):
    with io.StringIO() as csvfile:
        fieldnames = column_order
        writer = csv.DictWriter(csvfile, 
	                            fieldnames=fieldnames, 
				                extrasaction='ignore')

        writer.writeheader()
        for row in time_group:
            writer.writerow(row)

        return csvfile.getvalue()
