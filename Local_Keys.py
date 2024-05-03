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

def Get_Assistant_ID() -> str:
    # Get current json data
    with open('Local_Keys.json', 'r') as file:
        data = json.load(file)

    # Return vector store id
    return data["assistant_id"]

def Set_Assistant_ID(assistantID:str) -> None:
    # Get current json data
    with open('Local_Keys.json', 'r') as file:
        data = json.load(file)

    # Update json data
    data["assistant_id"] = assistantID

    # Write updated json data
    with open('Local_Keys.json', 'w') as file:
        json.dump(data, file)

def Get_Vector_Store_ID() -> str:
    # Get current json data
    with open('Local_Keys.json', 'r') as file:
        data = json.load(file)

    # Return vector store id
    return data["vector_store_id"]

def Set_Vector_Store_ID(vectorStoreID:str) -> None:
    # Get current json data
    with open('Local_Keys.json', 'r') as file:
        data = json.load(file)

    # Update json data
    data["vector_store_id"] = vectorStoreID

    # Write updated json data
    with open('Local_Keys.json', 'w') as file:
        json.dump(data, file)