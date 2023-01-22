import json

def ReadFile(filePath):
    with open(filePath, 'r') as f: # File object
        data = json.load(f) # Json data
        f.close()
        return data

def SaveFile(filePath, data):
    dataDump = json.dumps(data, indent=4)
    f = open(filePath, "w")
    f.write(data)
    f.close()
