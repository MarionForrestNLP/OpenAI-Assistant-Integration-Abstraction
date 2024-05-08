# Imports
import json
import Local_Keys as LK

from openai import OpenAI

# Constants
ASSISTANT_TEMPERATURE = 1.4
ASSISTANT_MODEL = "gpt-3.5-turbo-0125"
ASSISTANT_NAME = "NLPete"
MESSAGE_HISTORY_LENGTH = 25
MAX_PROMPT_TOKENS = 5000
VECTOR_STORAGE_TIME = 1 # in  terms of days
VECTOR_STORE_LIST_LIMIT = 50

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
    filePaths = json.load(open('Vector_Store_Files.json', 'r'))["filePaths"]
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
            "days": VECTOR_STORAGE_TIME
        }
    )

    # Save vector store id
    LK.Set_Vector_Store_ID(vectorStore.id)

    # return vector store
    return vectorStore
# Function End

"""
Assistant Object

This class is used to interact with the OpenAI Assistant. This class has methods for sending and
receiving messages.

Properties
    ast_Client (OpenAI): The OpenAI client instance
    ast_Intance (dict): The OpenAI Assistant instance
    ast_Thread (dict): The Assistant Thread instance
    ast_Tool_Set (list): A list of tool dictionaries
    ast_Tool_Resources (dict): A dictionary of tool resources

Methods
    Add_File_To_Vector_Store(file_path:str)
    Update_Tool_Set(tool_Set:list, tool_Resources:dict)
    Delete_Assistant()
    Send_Message(message_content:str, message_attachments:list=[])
    Get_Message_History()
"""
class Assistant:
    # Properties
    ast_Client = None
    ast_Model = None
    ast_Name = None
    ast_Instructions = None
    ast_Tool_Set = []
    ast_Tool_Resources = {}
    ast_User_Defined_Functions = {}
    ast_Model_Parameters = {
        "temperature": 1.0,
        "top_p": 1.0
    }
    ast_Intance = None
    ast_Thread = None

    # Constructor
    def __init__(self, client:OpenAI, assistant_name:str, instruction_prompt:str,
                 tool_Set:list, tool_Resources:dict, function_Dictionary:dict={},
                 model:str=ASSISTANT_MODEL, temperature:float=ASSISTANT_TEMPERATURE,) -> None:
        
        # Set properties
        self.ast_Client = client
        self.ast_Model = model
        self.ast_Name = assistant_name
        self.ast_Instructions = instruction_prompt
        self.ast_Tool_Set = tool_Set
        self.ast_Tool_Resources = tool_Resources
        self.ast_User_Defined_Functions = function_Dictionary
        self.ast_Model_Parameters["temperature"] = temperature

        # Create assistant
        self.ast_Intance = self.ast_Client.beta.assistants.create(
            model=self.ast_Model,
            name=self.ast_Name,
            instructions=self.ast_Instructions,
            tools=self.ast_Tool_Set,
            tool_resources=self.ast_Tool_Resources,
            temperature=self.ast_Model_Parameters["temperature"],
        )

        # Initialize thread
        self.ast_Thread = client.beta.threads.create()
    # Constructor End

    # \/ \/ Methods \/ \/

    """
    Deletes the assistant. Call this method once you are done using the assistant.

    Parameters
        None

    Returns
        deletion_object.status (bool): The status of the operation
    """
    def Delete_Assistant(self) -> bool:
        # get assistant id
        assistant_id = self.ast_Intance.id

        # Delete assistant
        deletion_object = self.ast_Client.beta.assistants.delete(
            assistant_id=assistant_id
        )

        # update instance
        self.ast_Intance = None

        # return status
        return deletion_object.deleted
    # Function End

    """
    Adds a file to the assistant's vector store.

    Parameters
        file_path (str): The path to the file

    Returns
        vector_file.status (str): The status of the operation
    """
    def Add_File_To_Vector_Store(self, file_path:str) -> str:
        # get vector store
        vector_store_id = self.ast_Tool_Resources["file_search"]["vector_store_ids"][0]

        # create file object
        file_object = self.ast_Client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants"
        )

        # add file to vector store
        vector_file = self.ast_Client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_object.id
        )

        # return status
        return vector_file.status
    # Function End

    """
    Updates the assistant's tools and resources.

    Parameters
        tool_Set (list): A list of tool dictionaries
        tool_Resources (dict): A dictionary of tool resources

    Returns
        (bool): The completions status of the operation
    """
    def Update_Tool_Set(self, tool_Set:list[dict], tool_Resources:dict) -> bool:
        try:
            # Update tool set
            updated_assistant = self.ast_Client.beta.assistants.update(
                assistant_id=self.ast_Intance.id,
                tools=tool_Set,
                tool_resources=tool_Resources
            )

            # update intance
            self.ast_Intance = updated_assistant
            self.ast_Tool_Set = tool_Set
            self.ast_Tool_Resources = tool_Resources

            # return status
            return True
        except:
            # return status
            return False
    # Function End

    """
    Adds a new message to the assistant's thread
    and returns the new message object. Also adds
    attachments to the message if any are passed.

    Parameters
        message_content (str): The text content of the message
        message_attachments (list): A list of attachment dictionaries.
            Defaults to an empty list.

    Returns
        message (dict): The new message object
    """
    def Send_Message(self, message_content:str, message_attachments:list[dict] = [None]) -> dict:
        # Variable initialization
        message = None

        # Has attachments
        try:
            # Format attachments
            formatted_message_attachments = [None]
            if message_attachments[0] is not None:
                for attachment in message_attachments:
                    formatted_message_attachments.append({
                        "file_id": attachment.id,
                        "tools": [{"type": "file_search"}]
                    })
                # Loop end
            
            # Create message
            message = self.ast_Client.beta.threads.messages.create(
                thread_id=self.ast_Thread.id,
                role="user",
                content=message_content,
                attachments=formatted_message_attachments
            )

        # Does not have attachments
        except:
            # Create message
            message = self.ast_Client.beta.threads.messages.create(
                thread_id=self.ast_Thread.id,
                role="user",
                content=message_content
            )

        # Return message object
        finally:
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
                self.__Handle_Function_Calls(self.ast_Client, local_Run, pending_Functions)

        # get history
        message_History = self.ast_Client.beta.threads.messages.list(
            thread_id=self.ast_Thread.id,
            limit=MESSAGE_HISTORY_LENGTH,
            order="asc"
        ).data

        # return history
        return message_History
    # Function End

    def __Handle_Function_Calls(self, client, runInstance, functionObjectList) -> None:
        # Iterate through each function call
        for functionObject in functionObjectList:
            functionObjectDict = dict(functionObject)

            # Get function details
            functionDetails = dict(functionObjectDict['function'])

            # Get arguments
            argumentSet = json.loads(functionDetails['arguments'])
            args = list(argumentSet.values())

            # Call functions
            for functionName in self.ast_User_Defined_Functions.keys():
                if functionName == functionDetails["name"]:
                    try:
                        # Import libray
                        exec(self.ast_User_Defined_Functions[functionName][0])

                        # Build funciton call
                        function_call_string = self.ast_User_Defined_Functions[functionName][1] + "("
                        for i in range(self.ast_User_Defined_Functions[functionName][2]):
                            if i != 0:
                                function_call_string = function_call_string + ", "
                            function_call_string = function_call_string + "\'" + args[i] + "\'"
                        function_call_string = function_call_string + ")"

                        # Execute function
                        returnObject = eval(function_call_string)
                    except Exception as e:
                        print(e)
                        # Return fail case
                        returnObject = self.ast_User_Defined_Functions[functionName][3]
            # Loop End

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

# Class End