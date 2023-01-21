import json

def ReadFile(filePath):
    with open(filePath, 'r') as f: # File object
        data = json.load(f) # Json data
        f.close()
        return data
