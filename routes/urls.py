from django.urls import path
from .views import ( # At this point just import the whole module.
    route_lists_json,
    csv_drop_off, 
    documents_menu, 
    frozen_tickets,                 
    fulfillment_tickets_json, 
    fulfillment_vue_page,
    post_csv, 
    route_lists, 
    fulfillment_menu, 
    download_csv, 
    select_date, 
    select_time, 
    upload_error, 
    fulfillment_options,
    add_warehouse,
    fulfillment_navagation,
    create_depot,
    post_depot,
    )


urlpatterns = [
    # Paths for the create route docs workflow
    path('', fulfillment_menu, name='fulfillment-menu'),
    path('drop-order/', csv_drop_off, name='drop-off'),
    path('post-csv/', post_csv, name='post-csv'),
    
    path('document-navigation/', documents_menu, name='document-navigation'),
    path('update-warehouse', fulfillment_options, name='update-warehouse'),
    path('post-warehouse', add_warehouse, name='post-warehouse'),

    path('fulfillment-tickets', fulfillment_vue_page, name='fulfillment-tickets'),
    path('fulfillment-tickets-json', fulfillment_tickets_json, name='fulfillment-tickets-json'),
    path('fulfillment-tickets-vue', fulfillment_vue_page, name='fullfillment-tickets-vue'),
    path('fulfillment-navagation', fulfillment_navagation, name='fulfillment-navagation'),
    path('frozen-tickets', frozen_tickets, name='frozen-tickets'),
    path('upload-error', upload_error, name='upload-error'),

    path('create-depot', create_depot, name='create-depot'),
    path('post-depot', post_depot, name='post-depot'),
    path('route-lists', route_lists, name='route-lists'),
    path('route-lists-json', route_lists_json, name='route-lists-json'),

    # Paths for the download deliveries workflow
    path('select-date', select_date, name='select-date'),
    path('select-time', select_time, name='select-time'),
    path('download-csv/<str:time>', download_csv, name='download-csv'),
]

"""
    'drop-off' -> 'post-csv' -> 'create documents nav page' Y
        'box build documents nav'
            'create warehouse page' -> 'build documents nav' Y
                'fulfillment tickets'
                'frozen orders'
        'delivery documents'
            'select drivers page' -> 'route lists'
"""