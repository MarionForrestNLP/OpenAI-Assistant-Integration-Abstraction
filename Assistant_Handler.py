# Imports
import Assistant
import json
import Local_Keys as Put_Your_API_Key
import time
from openai import OpenAI

def Build_Assistant() -> Assistant.Assistant:
    # Connect to the OpenAI API
    openaiClient = OpenAI(api_key=Put_Your_API_Key.Here()) # Put your API key here

    # Run maintainence
    Delete_Old_Vectors(openaiClient)

    # Create an assistant
    assistant = Assistant.Assistant(
        client=openaiClient,
        assistant_name="NLPete",
        instruction_prompt=Get_Assistant_Context(),
        tool_set=Get_Assistant_Tools(),
        function_dictionary=Get_Function_Dictionary(),
        model="gpt-3.5-turbo-0125",
        model_parameters={"temperature": 1.4, "top_p": 1.0}
    )

    # Add files to assistant's vector store
    assistant.Add_File_To_Vector_Store(r"NLP_Logix_Company_Fact_Sheet.docx")

    # return assistant
    return assistant


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

def Delete_Old_Vectors(client:OpenAI, days:int=2) -> None:
    files = client.files.list()

    for file in files.data:
        if file.created_at < (time.time() - (days * 86400)):
            client.files.delete(file.id)
        else:
            continue

    vectorStores = client.beta.vector_stores.list(limit=100)

    for vectorStore in vectorStores.data:
        if vectorStore.created_at < (time.time() - (days * 86400)):
            client.beta.vector_stores.delete(vectorStore.id)
        elif vectorStore.status == "expired":
            client.beta.vector_stores.delete(vectorStore.id)
        else:
            continue

def Delete_Old_Assistants(client:OpenAI, days:int=2) -> None:
    assistants = client.beta.assistants.list(limit=100)

    for assistant in assistants.data:
        if assistant.created_at < (time.time() - (days * 86400)):
            client.beta.assistants.delete(assistant.id)
        else:
            continue

def Get_Function_Dictionary() -> dict:
    functionDict = {
        "Record_Client_Email": (
            "import Assistant_Functions",
            "Assistant_Functions.Record_Client_Email",
            2,
            "False"
        ),
        "Unanswerable_Question": (
            "import Assistant_Functions",
            "Assistant_Functions.Unanswerable_Question",
            1,
            "False"
        ),
    }

    return functionDict