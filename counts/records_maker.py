import pandas as pd
from pathlib import Path
import json

def serialize(records_list, table_name):
    return [{'model': table_name, 
     'pk': i,
     'fields': fields} for i, fields in enumerate(records_list)]

def dump_records(dictionary, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(dictionary))

#Load the file and clean up the names.
menus = pd.read_csv(
    Path(Path.home(), 'Gleaners Community Food Bank', 
    'Healthcare Programs - Healthcare Working Directory', 'menumatrix.csv'))

menus = menus.rename(mapper={'Item Code':'item_code', 
                             'Description':'description', 
                             'Storage':'storage'}, axis=1)

#Wraps the records in the necessary structure. MUST BE A FRESH DB FOR THIS.

#Create the join table records
melted = menus.melt(id_vars='item_code', 
                    value_vars = menus.columns[3:], 
                    var_name='menu', 
                    value_name='quantity')
join_records = melted[melted['quantity'] != 0].to_dict(orient='records')

#Create product records
products = menus[menus.columns[:3]].copy()
product_records = products.to_dict(orient='records')

#Create menu records
menu_records = [{'description': description} 
                for description in menus.columns[3:]]

dump_records(serialize(menu_records, 'counts.menus'), 'menus.json')
dump_records(serialize(product_records, 'counts.records'), 'products.json')
dump_records(serialize(join_records, 'counts.share'), 'menu_product_join.json'))