import getpass
from pathlib import Path
import json
from urllib.parse import urljoin
import pandas as pd
from shareplum import Site, Office365
from shareplum.site import Version

def get_app_password():
    secrets_path = Path(Path.home(), 'Desktop', 'Secrets', 'HealthcareSecrets.json')
    with open(secrets_path) as f:
        secrets = json.load(f)
    username = 'mvickers@gcfb.org'
    password = secrets['password']

    return username, password

def get_sharepoint_files_site(base_url, site_url, username, password):
    authcookie = Office365(
        base_url, username=username, password=password).GetCookies()
    return Site(site_url, authcookie=authcookie, version=Version.v365)

def get_sharepoint_list_site(base_url, site_url, username, password):
    authcookie = Office365(
        base_url, username=username, password=password).GetCookies()
    return Site(site_url, authcookie=authcookie)

def load_df_from_sharepoint(
    base_url, site_url, list_name, view_name, username, password):
    site = get_sharepoint_list_site(base_url, site_url, username, password)
    sp_list = site.List(list_name)
    deliveries = sp_list.get_list_items(view_name=view_name)

    print(f'Loaded {list_name} successfully.')

    return pd.DataFrame(deliveries)

def make_date_folder(day, time, site, root_folder):
    date_string = str(day.strftime("%m-%d-%Y"))
    if time:
        dir_name = urljoin(root_folder, date_string, time)
    else:
        dir_name = urljoin(root_folder, date_string)

    folder = site.Folder(dir_name) 

    return folder