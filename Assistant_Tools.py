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

"""
Returns a dictionary containing the assistant's resources.
Currently, only "file_search" is supported.

Parameters
    client (OpenAI): The OpenAI client

Returns
    toolResources (dict): A dictionary containing the assistant's resources
"""
def Get_Tool_Resources(client:OpenAI) -> dict:
    # Initialize return object
    toolResources = {}

    # Get tools
    toolSet = Get_Assistant_Tools()
    
    # Iterate through the tools
    for tool in toolSet:
        if tool["type"] == "file_search":
            # Add file search resources
            toolResources.update(Get_File_Search_Resources(client))

    # return resources
    return toolResources
# Function End

"""
Creates a dict with a vector store id to be used by the file search tool.

Parameters
    client (OpenAI): The OpenAI client

Returns
    vectorStore (dict): A dictionary containing the file search resource
"""
def Get_File_Search_Resources(client:OpenAI) -> dict:
    # Initialize return object
    returnVectorStore = {}

    # Get a list of vertor stores
    vectorStoreList = client.beta.vector_stores.list().data

    # Iterate through vector stores
    for vectorStore in vectorStoreList:
        if vectorStore.status != "expired":
            returnVectorStore = vectorStore
            break
        else:
            continue
    # Loop end

    if returnVectorStore == {}:
        # Create new vector store
        returnVectorStore = Create_Vector_Store(client)

    returnDict = {
        "file_search": {
            "vector_store_ids": [returnVectorStore.id]
        }
    }

    # return
    return returnDict
# Function End

"""
Creates a new vector store and saves the VS's id to a json file.

Parameters
    client (OpenAI): The OpenAI client

Returns
    vectorStore (dict): A dictionary containing the assistant's resources"""
def Create_Vector_Store(client:OpenAI):
    # Create and array of file IDs
    filePaths = [r"./NLP_Logix_Company_Fact_Sheet.docx"]
    fileIDs = []
    for filePath in filePaths:
        # Upload info files
        fileObject = client.files.create(
            file=open(filePath, "rb"),
            purpose="assistants"
        )

        # Append file ID
        fileIDs.append(fileObject.id)

    # Create vector store
    vectorStore = client.beta.vector_stores.create(
        name="Company_Fact_Sheets",
        file_ids=fileIDs,
        expires_after={
            "anchor": "last_active_at",
            "days": 1
        }
    )

    # return vector store
    return vectorStore
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