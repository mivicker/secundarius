import pandas as pd
from pathlib import Path
import json

# This is broken code, but it shows the process by which I created
# the json necessary to be loaded into the django database from
# the planning documents.

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

#Once these are completed, them we can run this code

base_path = Path(Path.home(), 'Desktop', 'secundarius')

with open(Path(base_path, 'product_mapper.json'), 'r') as f:
    prod_mapper = json.load(f)
    
with open(Path(base_path, 'menu_mapper.json'), 'r') as f:
    menu_mapper = json.load(f)

def update(record, field, value):
    record[field] = value
    return record

with_menu_pks = [update(record, 'menu', menu_mapper[record['menu']]) for record in join_records]
share_records = [update(record, 'product', prod_mapper[record['product']]) for record in join_records]

dump_records(serialize(share_records, 'counts.share'), 'shares.json')