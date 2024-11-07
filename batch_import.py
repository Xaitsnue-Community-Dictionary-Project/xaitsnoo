from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os
import pathlib

def initialize_sheets_api(api_key):
    service = build('sheets', 'v4', developerKey=api_key)
    return service

def get_sheets(service, id):
    spreadsheets = {}
    index = service.spreadsheets().values().get(spreadsheetId=id, range='sheet1!A:Z').execute().get('values', [])
    for i in index:
        name = i[0]
        sheet_id = i[1]
        spreadsheets[name] = sheet_id
    
    return(spreadsheets)

def read_sheets(sheets):
    
    all_vals = []
    for i in sheets.values():
        x = service.spreadsheets().get(spreadsheetId=i).execute()
        sheet_names = sheets_within_sheets(x)
        for j in sheet_names:
            subsheet_range = j + '!A:Z'
            result = service.spreadsheets().values().get(spreadsheetId=i, range=subsheet_range).execute()
            values = result.get('values', [])
            
            #only adding non-null sheets
            if values != []:
                curr_val = []
                for k in range(len(values[0])):
                    if values[k][0] != '':
                        
                        #delete variant and context columns, can change this when we figure out how to account for them
                        temp = [values[k][i] for i in range(len(values[k])) if i != 3 and i != 4]
                        curr_val.append(temp)
                        
                all_vals.append(curr_val)

    #column headers = ['headword', 'English', 'grammar', 'speakers', 'other info', 'semantic domain']
    return(all_vals)
                
            
        
def sheets_within_sheets(x):
    #Gets all of the subsheets within the Google Sheet x
    sheets = x.get('sheets', [])
    sheet_names = [sheet['properties']['title'] for sheet in sheets]
    return sheet_names

load_dotenv(dotenv_path=pathlib.Path().resolve()/'google_api_key.env')
api_key = os.getenv('GOOGLE_API_KEY')

# ID for Google Sheet that contains all of the sheet ids 
id = '1isc2rari_iO6Djpds51hxcU8CHUIGCRV1rUAp5XE_wk'

# Initializes the google sheets API
service = initialize_sheets_api(api_key)

# Returns a dictionary of the sheet names and their respective ids for all 
# of the sheets contained in the batch import index sheet
sheets = get_sheets(service, id)

# Returns the values for all of the subsheets as a 2d list
all_sheets = read_sheets(sheets)