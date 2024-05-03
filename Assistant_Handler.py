# Imports
import json
import Local_Keys as LK
import Assistant_Functions as AF

from openai import OpenAI

# Constants
ASSISTANT_TEMPERATURE = 1.4
ASSISTANT_MODEL = "gpt-3.5-turbo-0125"
ASSISTANT_NAME = "NLPete"
MESSAGE_HISTORY_LENGTH = 25
MAX_PROMPT_TOKENS = 5000

# \/ \/ Functions \/ \/ 

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
    # Initialize vector store
    vectorStore = None
    
    try:
        # Try to retrieve a prexisting vector store
        vectorStore = client.beta.vector_stores.retrieve(
            vector_store_id=LK.Get_Vector_Store_ID()
        )

        # Check expiration
        if vectorStore.status == "expired":
            vectorStore = Create_Vector_Store(client)
    except:
        # Create new vector store
        vectorStore = Create_Vector_Store(client)
    finally:
        # Create file search resources
        returnDict = {
            "file_search": {
                "vector_store_ids": [vectorStore.id]
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
    filePaths = json.load(open('Vector_Store_Files.json', 'r'))[filePaths]
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

    # Save vector store id
    LK.Set_Vector_Store_ID(vectorStore.id)

    # return vector store
    return vectorStore
# Function End

"""
Initializes the assistant. Try's the retrieve the assistant. If it doesn't exist,
it creates a new one and saves the ID to a json file.

Parameters
    client (OpenAI): The OpenAI client

Returns
    assistant (dict): A dictionary containing the assistant's resources
"""
def Assistant_Initializer(client:OpenAI, instructionPrompt:str, toolSet:list, toolResources:dict) -> dict:
    # Initialize Assistant
    assistant = None

    try:
        # Retrieve Assistant
        assistant = client.beta.assistants.retrieve(
            assistant_id=LK.Get_Assistant_ID()
        )

        # Update Assistant
        assistant = client.beta.assistants.update(
            assistant_id=LK.Get_Assistant_ID(),
            temperature=ASSISTANT_TEMPERATURE,
            instructions=instructionPrompt,
            tools=toolSet,
            tool_resources=toolResources
        )
    
    except:
        # Create Assistant
        assistant = client.beta.assistants.create(
            name=ASSISTANT_NAME,
            model=ASSISTANT_MODEL,
            temperature=ASSISTANT_TEMPERATURE,
            instructions=instructionPrompt,
            tools=toolSet,
            tool_resources=toolResources
        )

        # Save Assistant
        LK.Set_Assistant_ID(assistant.id)

    finally:
        # return assistant
        return assistant
# Function End

"""
This function attempts to identify and handle function calls.
If a function is called it will execute the function and pass it's
return value to the run instance.

Parameters
    client (OpenAI): The OpenAI client
    runInstance (dict): The run instance
    functionObjectList (list): A list of function objects

Returns
    None
"""
def Handle_Function_Calls(client, runInstance, functionObjectList) -> None:
    # Iterate through each function call
    for functionObject in functionObjectList:
        functionObjectDict = dict(functionObject)

        # Get function details
        functionDetails = dict(functionObjectDict['function'])

        # Get arguments
        argumentSet = json.loads(functionDetails['arguments'])
        argumentValues = list(argumentSet.values())

        # Call functions
        returnObject = None
        if functionDetails["name"] == "Record_Client_Email":
            try:
                returnObject = AF.Record_Client_Email(argumentValues[0], argumentValues[1])
            except:
                returnObject = "False"

        # Update run instance
        updatedRun = client.beta.threads.runs.submit_tool_outputs(
            thread_id=runInstance.thread_id,
            run_id=runInstance.id,
            tool_outputs=[
                {
                    "tool_call_id": functionObjectDict["id"],
                    "output": returnObject
                }
            ]
        )
    # Loop End

    return None
# Function End

"""
Assistant Object

This class is used to interact with the OpenAI Assistant.

Properties
    ast_Client (OpenAI): The OpenAI client instance
    ast_Intance (dict): The OpenAI Assistant instance
    ast_Thread (dict): The Assistant Thread instance
"""
class Assistant:
    # Properties
    ast_Client = None
    ast_Intance = None
    ast_Thread = None

    # Constructor
    def __init__(self, client:OpenAI, instructionPrompt:str, toolSet:list, toolResources:dict) -> None:
        # Set client
        self.ast_Client = client

        # Initialize assistant
        self.ast_Intance = Assistant_Initializer(
            client=client,
            instructionPrompt=instructionPrompt,
            toolSet=toolSet,
            toolResources=toolResources
        )

        # Initialize thread
        self.ast_Thread = client.beta.threads.create()
    # Constructor End

    # \/ \/ Methods \/ \/
    """
    Adds a new message to the assistant's thread
    and returns the new message object.

    Parameters
        userInput (str): The user's input

    Returns
        message (dict): The new message object
    """
    def Send_Message(self, user_Input:str) -> dict:
        # Add user input to thread
        message = self.ast_Client.beta.threads.messages.create(
            thread_id=self.ast_Thread.id,
            role="user",
            content=user_Input,
        )

        # Return message object
        return message
    # Function End

    """
    Gets the assistant's message history
    and returns a list of message objects.

    Parameters
        None

    Returns
        history (list): A list of message objects
    """
    def Get_Message_History(self) -> list:
        # get the current run instance of the thread
        local_Run = self.ast_Client.beta.threads.runs.create(
            thread_id=self.ast_Thread.id,
            assistant_id=self.ast_Intance.id,
            max_prompt_tokens=MAX_PROMPT_TOKENS
        )

        # check if run is complete
        while local_Run.status != "completed":
            local_Run = self.ast_Client.beta.threads.runs.retrieve(
                thread_id=self.ast_Thread.id,
                run_id=local_Run.id
            )

            # check for pending functions
            if local_Run.status == "requires_action":
                pending_Functions = local_Run.required_action.submit_tool_outputs.tool_calls

                # handle function calls
                Handle_Function_Calls(self.ast_Client, local_Run, pending_Functions)

        # get history
        message_History = self.ast_Client.beta.threads.messages.list(
            thread_id=self.ast_Thread.id,
            limit=MESSAGE_HISTORY_LENGTH,
            order="asc"
        ).data

        # return history
        return message_History
    # Function End

    # \/ \/ Getters and Setters \/ \/
    def Get_Instance(self) -> dict:
        return self.ast_Intance