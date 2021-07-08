import pandas as pd
from pathlib import Path

# This script converts the menumatrix that was developed
# during Henry's groceries planning phase to three
# json files that can be loaded into the database.

menus = pd.read_csv(
    Path(Path.home(),
     'Gleaners Community Food Bank', 
     'Healthcare Programs - Healthcare Working Directory', 
     'menumatrix.csv'))

menus = menus.rename(mapper={'Item Code':'item_code', 
                             'Description':'description', 
                             'Storage':'storage'}, axis=1)
 
#Create the join table records
melted = menus.melt(id_vars='item_code', 
                    value_vars = menus.columns[3:], 
                    var_name='menu', 
                    value_name='quantity')
melted['pk'] = range(len(melted))
melted[melted['quantity'] != 0].to_json(
	'menu_product_join.json', orient='records')

#Create product records
products = menus[menus.columns[:3]].copy()
products['pk'] = range(len(products))
products.to_json('products.json', orient='records')

#Create menu records
(pd.concat([pd.Series(menus.columns[3:]), pd.Series(range(len(menus)))], axis=1)
    .rename(mapper={0: 'description', 1: 'pk'}, axis=1)
    .dropna()
    .to_json('menus.json', orient='records'))