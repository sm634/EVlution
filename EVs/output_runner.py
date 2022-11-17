"""
The output runner takes in all of the data from a given model simulation run block, with the csv's which are saved in
the EVs/Data folder, combines all model and agent level data, while creating the seed rep of that data extracted from
the structure of the file name, and pushes this enriched output data to a designated database.
"""
from db_access import DBAccess
import pandas as pd
import os
import re


files = os.listdir('Data/')


def extract_seed(text: str):
    """
    Extracting the seed number from the output file.
    """
    text = text[::-1]
    seed_match = re.search(r'vsc.\d+_', text)
    if seed_match:
        seed = seed_match.group().replace('_', '').replace('vsc.', '')
        seed = seed[::-1]
        return seed


def df_to_db():
    # instantiate dbaccess.
    dbaccess = DBAccess()

    # set up dataframes for all outputs belonging to mdf and adf.
    mdf_df = pd.DataFrame()
    adf_df = pd.DataFrame()
    for file in files:
        seed_no = extract_seed(file)
        df = pd.read_csv(file)
        df['seed'] = seed_no
        if re.match(r'mdf_', file):
            mdf_df.append(df)
        elif re.match(r'adf_', file):
            adf_df.append(df)

    dbaccess.write_to_db(mdf_df, 'mdf_output')
    dbaccess.write_to_db(adf_df, 'adf_output')


df_to_db()
