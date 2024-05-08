import json

def Get_API_Key() -> str:
    # Get current json data
    with open('Local_Keys.json', 'r') as file:
        data = json.load(file)

    # Return api key
    return data["api_key"]

def Get_Org_ID() -> str:
    # Get current json data
    with open('Local_Keys.json', 'r') as file:
        data = json.load(file)

    # Return org id
    return data["org_id"]