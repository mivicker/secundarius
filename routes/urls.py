from django.urls import path
from .views import (csv_drop_off, documents_menu, frozen_tickets, 
                    fulfillment_tickets, post_csv, route_lists, 
                    fulfillment_menu, download_csv, select_date, 
                    select_time)

urlpatterns = [
    # Paths for the create route docs workflow
    path('', fulfillment_menu, name='fulfillment-menu'),
    path('drop-order/', csv_drop_off, name='drop-off'),
    path('post-csv/', post_csv, name='post-csv'),
    path('doc-menu/', documents_menu, name='doc-menu'),
    path('fullfillment/', fulfillment_tickets, name='pack-tickets'),
    path('lists/', route_lists, name='route-lists'),
    path('frozen-list', frozen_tickets, name='frozen-list'),

    # Paths for the download deliveries workflow
    path('select-date', select_date, name='select-date'),
    path('select-time', select_time, name='select-time'),
    path('download-csv/<str:time>', download_csv, name='download-csv'),
]