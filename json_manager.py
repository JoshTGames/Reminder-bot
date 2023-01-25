import json

def ReadFile(filePath):
    with open(filePath, 'r') as f: # File object
        data = json.load(f) # Json data
        f.close()
        return data

def WriteFile(filePath, data):
    with open(filePath, 'w') as f: # File object    
        newData = json.dumps(data, indent=4)
        f.write(newData)
        f.close()