from django.conf import settings
from shareplum import Site, Office365

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