from django.urls import path
from .views import (csv_drop_off, documents_menu, download_deliveries, 
                          frozen_tickets, fulfillment_tickets, post_csv, 
                          route_lists, fulfillment_menu)

urlpatterns = [
    path('fulfillment-menu/', fulfillment_menu, name='fulfillment-menu'),
    path('drop-order/', csv_drop_off, name='drop-off'),
    path('post-csv/', post_csv, name='post-csv'),
    path('doc-menu/', documents_menu, name='doc-menu'),
    path('fullfillment/', fulfillment_tickets, name='pack-tickets'),
    path('lists/', route_lists, name='route-lists'),
    path('frozen-list', frozen_tickets, name='frozen-list'),
    path('download-deliveries', download_deliveries, name='download-deliveries'),
]