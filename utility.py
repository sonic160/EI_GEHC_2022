### Version: 20220602 by ZZG ###
### Created with features of reading data of the parts


### Import the needed packages. ###
import pandas as pd
from datetime import datetime


### This subfunction integrates all the utilities to read the data, and do the necessary preprocessing. ###
# Input: filename: A string indicating the path of the file to be read.
# Output: * df_org - Dataframe containing the original data from sheet "Failure Data"
#         * df_part - Dataframe containing the part failure data.
#         * df_comp_f - Dataframe containing the components that failed.
#         * df_comp_c - Dataframe containing the components that are cosmetically replaced.
#         * df_comp_ttf - Dataframe containing the time to failure/censoring time for the failed components. If there is an "F", it is time to failure; if it is 0, it is censoring time.
#         * df_part_info - Dataframe containing auxilliary information on the parts (total number, e.g.)
def get_data_from_excel(filename):
    ### Original data ###
    # Read all the data into a dataframe.
    df_org = pd.read_excel(filename)

    return df_org


### This subfunction reads part data, and extract the time to failure/censoring time.
# Input: filename: A string indicating the path of the file to be read.
# Output: A dataframe containing the part data
def get_part_data(filename):
    # Read all the data
    df_org = get_data_from_excel(filename)

    # Add a column to record the repair history.
    df_part = df_org.copy()
    df_part.insert(2, 'Repair History', 'Repaired')
    df_part.loc[df_part.loc[:, 'Previous repair po'] == 'MFG', 'Repair History'] = 'Prime'

    # Add a column to record the censoring state.
    df_part.insert(2, 'Censoring', 0)

    # Sort by SN
    df_part = df_part.sort_values(by='SN')
    df_part = df_part.reset_index(drop=True)

    # Get the part version.
    for i in range(df_part.shape[0]):
        if df_part.loc[i, 'ITEM'][-2:] == '-R':
            df_part.loc[i, 'ITEM'] = df_part.loc[i, 'ITEM'][:-2]
        
    # Define the current time for calculating the censoring time.
    current_time = datetime(2022, 6, 3, 0, 0)

    for i in range(df_part.shape[0]-1):
        # Check if since the previous repair, the part is still surviving.
        if df_part.loc[i, 'SN'] != df_part.loc[i+1, 'SN']:
            duration = current_time - datetime.strptime(df_part.loc[i, 'Repair Date'], '%Y-%m-%d')
            df_part = df_part.append({'SN': df_part.loc[i, 'SN'], 'Duration(days)': duration.days,
            'Repair History': 'Repaired', 'Censoring': 1,
            'ITEM': df_part.loc[i, 'ITEM']}, ignore_index=True)

    # The last row.
    i+=1
    duration = current_time - datetime.strptime(df_part.loc[i, 'Repair Date'], '%Y-%m-%d')
    df_part = df_part.append({'SN': df_part.loc[i, 'SN'], 'Duration(days)': duration.days, 
    'Repair History': 'Repaired', 'Censoring': 1,
    'ITEM': df_part.loc[i, 'ITEM']}, ignore_index=True)

    # Keep only the necessary columns.
    df_part = df_part.sort_values(by=['SN', 'Censoring'])
    df_part = df_part.reset_index(drop=True)
    df_part = df_part[['SN', 'Censoring', 'Repair History', 'Duration(days)', 'ITEM']]
    
    return df_part


if __name__ == '__main__':
    filename = r'C:\Users\Zhiguo\OneDrive - CentraleSupelec\Code\Python\ge_case_study\2022_ST4\XFD_freq_replacement - Names.xlsx'
    df_part = get_part_data(filename)
