# Imports
import json
import time
from openai import OpenAI

"""
Reads a text file containing the assistant's context prompt.

Parameters
    None

Returns
    data (str): The assistant's context prompt
"""
def Get_Assistant_Context() -> str:
    # Open text file
    with open('Assistant_Context_Prompt.txt', 'r') as file:
        data = file.read()

    # Return data
    return data
# Function End

"""
Reads a json file containing the assistant's tools.

Parameters
    None

Returns
    data (list): A list of the assistant's tools
"""
def Get_Assistant_Tools() -> list:
    # Open json file
    with open('Assistant_Tools.json', 'r') as file:
        data = json.load(file)

    # Return data
    return data
# Function End

def Delete_Old_Vectors(client:OpenAI):
    files = client.files.list()

    for file in files.data:
        if file.created_at < (time.time() - (2 * 86400)):
            client.files.delete(file.id)
        else:
            continue

    vectorStores = client.beta.vector_stores.list()

    for vectorStore in vectorStores.data:
        if vectorStore.created_at < (time.time() - (2 * 86400)):
            client.beta.vector_stores.delete(vectorStore.id)
        elif vectorStore.status == "expired":
            client.beta.vector_stores.delete(vectorStore.id)
        else:
            continue

def Get_Function_Dictionary() -> dict:
    functionDict = {
        "Record_Client_Email": (
            "import Assistant_Functions",
            "Assistant_Functions.Record_Client_Email",
            2,
            "False"
        )
    }

    return functionDict