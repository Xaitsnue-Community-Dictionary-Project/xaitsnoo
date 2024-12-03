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

from peewee import *

db = MySQLDatabase('Xaitsnoo')
        
# Grammar table
class Grammar(Model):
    uuid = IntegerField(primary_key=True)
    grammar_type = CharField()

    class Meta:
        database = db

# SemanticDomain (Classifications) table
class Classification(Model):
    uuid = IntegerField(primary_key=True)
    class_name = CharField()

    class Meta:
        database = db

# Speaker table
class Speaker(Model):
    uuid = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField()

    class Meta:
        database = db

# Word (Dictionary) table
class Dictionary(Model):
    uuid = IntegerField(primary_key=True)
    headword = CharField()
    translation = CharField()
    grammar = ForeignKeyField(Grammar, backref='words')
    notes = TextField()

    class Meta:
        database = db

# Variants table
class Variant(Model):
    uuid = IntegerField(primary_key=True)
    variant = CharField()
    context = CharField()
    dictionary = ForeignKeyField(Dictionary, backref='variants')
    speaker = ForeignKeyField(Speaker, backref='variants')

    class Meta:
        database = db

# Dictionary-Speaker Association table (many-to-many)
class DictionarySpeakerAssociation(Model):
    dictionary = ForeignKeyField(Dictionary, backref='speakers')
    speaker = ForeignKeyField(Speaker, backref='dictionaries')

    class Meta:
        database = db

# Classification-Taxonomy table (many-to-many relationship)
class ClassificationTaxonomy(Model):
    classification = ForeignKeyField(Classification, backref='taxonomies')
    class_association = ForeignKeyField(Classification, backref='associated_classes')

    class Meta:
        database = db

# Dictionary-Classification Association table (many-to-many)
class DictionaryClassificationAssociation(Model):
    dictionary = ForeignKeyField(Dictionary, backref='classifications')
    classification = ForeignKeyField(Classification, backref='dictionaries')

    class Meta:
        database = db

# Audio table
class Audio(Model):
    uuid = IntegerField(primary_key=True)
    audio_file = CharField()

    class Meta:
        database = db

# Dictionary-Audio Association table (many-to-many)
class DictionaryAudioAssociation(Model):
    dictionary = ForeignKeyField(Dictionary, backref='audios')
    audio = ForeignKeyField(Audio, backref='dictionaries')

    class Meta:
        database = db

# Photo table
class Photo(Model):
    uuid = IntegerField(primary_key=True)
    photo_file = CharField()

    class Meta:
        database = db

# Dictionary-Photo Association table (many-to-many)
class DictionaryPhotoAssociation(Model):
    dictionary = ForeignKeyField(Dictionary, backref='photos')
    photo = ForeignKeyField(Photo, backref='dictionaries')

    class Meta:
        database = db

db.connect(os.getenv('DATABASE_URL'))
db.create_tables([Grammar, Classification, Speaker, Dictionary, Variant, DictionarySpeakerAssociation,
  ClassificationTaxonomy, DictionaryClassificationAssociation, Audio, DictionaryAudioAssociation,
  Photo, DictionaryPhotoAssociation])

for row in all_sheets[0][1:]:
    headword = row[0].strip()
    english = row[1].strip()
    grammar, g_created = Grammar.get_or_create(grammar_type=row[2].strip())
    speakers = row[3].split(", ")
    info = row[4].strip()
    classification, c_created = Classification.get_or_create(class_name=row[5].strip())
    dictionary = Dictionary.create(
        headword = headword,
        translation = english,
        grammar = grammar.uuid,
        classification = classification.uuid,
        notes = info
    )
    for speaker in speakers:
        print(speaker)
        s, s_created = Speaker.get_or_create(first_name=speaker.strip(), last_name="")
        DictionarySpeakerAssociation.create(speaker = s.uuid, dictionary = dictionary.uuid)