# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 08:36:11 2021

@author: zm176oos
"""

import pandas as pd
import numpy as np
import sql_connect


# %%


query = '''SELECT own, schooljaar, toets, dattoets, score, adviesvo, brin, vest, leerjrpo, sexe
  FROM [DM_1Cijfer].[dbo].[INP_STROMEN] 

  WHERE schooljaar >= 2018
  AND typ = 1 -- geldige inschrijving in PO
  AND leerjrpo = 8 -- selecteer groep 8 leerlingen
  AND toets != 0
''' 

query_labels = '''SELECT VAR_NAAM, VAR_VALUE, VAR_LABEL
  FROM [DM_1Cijfer].[dbo].[P_DOMEINWAARDEN]
  WHERE VAR_NAAM IN ('toets$$', 'adviesvo$$')
'''

# %%

# open data en variable codes uit 
data = sql_connect.open_data(query)
labels = sql_connect.open_data(query_labels)

# join labels 
#data_labeled = data.join(query_labels[query])

# bewaar toets en advies labels en codes in apart df
toets_label = labels[labels['VAR_NAAM'] == 'toets$$'][['VAR_VALUE', 'VAR_LABEL']]
advies_label = labels[labels['VAR_NAAM'] == 'adviesvo$$'][['VAR_VALUE', 'VAR_LABEL']]



# %%

# relabel
data_labeled = data.merge(toets_label, left_on = 'toets', right_on = 'VAR_VALUE').drop(['VAR_VALUE'], axis = 1)
data_labeled = data_labeled.rename(columns={'VAR_LABEL': 'toets_label'})
data_labeled = data_labeled.merge(advies_label, left_on = 'adviesvo', right_on = 'VAR_VALUE').drop(['VAR_VALUE'], axis = 1)
data_labeled = data_labeled.rename(columns={'VAR_LABEL': 'advies_label'})
data_labeled['sexe'] = data_labeled['sexe'].replace({1: 'Man', 2: 'Vrouw'}) # vervang sexecodes met labels

# voeg 0 toe aan vestcodes die korter zijn dan 2 tekens
data_labeled['vest'] = data_labeled['vest'].astype('string')
data_labeled['vest'] = np.where(data_labeled['vest'].str.len() == 1, '0' + data_labeled['vest'], data_labeled['vest'])


    