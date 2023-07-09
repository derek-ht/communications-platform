import json

# Loads data from 'database.json' file into initial object
def load(initial_object):
    try:
        with open('database.json', 'r', encoding = 'utf8') as FILE:
            return json.load(FILE)
    except:
        return initial_object

# Saves data from initial object into database.json file
def save(store):
    # Saving data store to database.json file
    with open('database.json', 'w', encoding = 'utf8') as FILE:
        json.dump(store, FILE)

