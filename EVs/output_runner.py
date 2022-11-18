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


def format_output(df):
    """
    format the mdf and adf files to write to database.

    parameters
    ----------
    df: pandas DataFrame
        the pandas DataFrame representation of an mdf or adf output
    """
    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.set_index('date_time')
    output_cols = [
        'model_name', 'COM', 'av_charge', 'completed_trip', 'dead_cars', 'charge_load', 'av_moving',
        'av_home', 'av_work', 'av_random', 'av_CP', 'lat', 'lon', 'seed', 'price', 'rep_agents', 'season'
    ]
    return df[output_cols]


def get_avg_df(df):

    cols = df.columns
    # get averages of the numeric column values
    df_group = df.groupby(by=['date_time', 'model_name']).mean()
    non_numeric_cols = set(cols) - set(df_group.columns)
    # restructure non-numeric columns for join.
    df_group2 = (df[non_numeric_cols]
                 .reset_index()
                 .drop_duplicates(subset=['date_time'])
                 ).set_index('date_time')
    # bring back all data based on datetime.
    df = df_group.join(df_group2, how='inner').drop(labels=['seed', 'model_name'], axis=1)
    df = df.reset_index().set_index('date_time')
    return df


def df_to_db():
    # instantiate dbaccess.
    dbaccess = DBAccess()

    # set up dataframes for all outputs belonging to mdf and adf.
    mdf_df_list = []
    adf_df_list = []
    for file in files:
        if re.match(r'mdf_', file):
            seed_no = extract_seed(file)
            path = f'Data/{file}'

            print('processing file: ', path)

            df = pd.read_csv(path)
            df = format_output(df)
            df['seed'] = seed_no
            mdf_df_list.append(df)

        if re.match(r'adf_', file):
            seed_no = extract_seed(file)
            path = f'Data/{file}'

            print('processing file: ', path)

            df = pd.read_csv(path)
            df = format_output(df)
            df['seed'] = seed_no
            adf_df_list.append(df)

    if len(mdf_df_list) > 0:
        mdf_df = pd.concat(mdf_df_list)
        print("Writing mdf_full_output to database")
        dbaccess.write_to_db(mdf_df, 'mdf_full_output')
        print("Full output completed writing to database")

        mdf_avg_df = get_avg_df(mdf_df)
        print("Writing mdf_avg_output to database")
        dbaccess.write_to_db(mdf_avg_df, 'mdf_avg_output')

    if len(adf_df_list) > 0:
        adf_df = pd.concat(adf_df_list)
        print("Writing adf_ files to database")
        dbaccess.write_to_db(adf_df, 'adf_output')


df_to_db()
