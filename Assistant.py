# Imports
import json
import Vector_Storage
from openai import OpenAI

# Constants
DEFAULT_MODEL = "gpt-3.5-turbo-0125"
DEFAULT_MESSAGE_HISTORY_LENGTH = 25
DEFAULT_MAX_PROMPT_TOKENS = 5000
DEFAULT_MODEL_PARAMETERS = {
    "temperature": 1.0,
    "top_p": 1.0
}

"""
Assistant Class

This class is designed to abstract interactions with the OpenAI Assistant

Properties
    client (OpenAI): The OpenAI client instance
    name (str): The name of the assistant
    instructions (str): The assistant's context prompt
    tool_set (list): A list of tool dictionaries
    user_defined_functions (dict): A dictionary of user defined functions
    model (str): The model to use for the assistant
    model_parameters (dict): The parameters for the model
    vector_store (Vector_Storage): The internal vector store
    intance (dict): The OpenAI Assistant instance
    thread (dict): The Assistant Thread instance

Methods
    Add_File_To_Vector_Store(file_path:str) -> str
    Update_Tool_Set(tool_set:list) -> bool
    Delete_Assistant() -> bool
    Send_Message(message_content:str, message_attachments:list=[]) -> dict
    Get_Message_History() -> list
    Get_Attributes() -> dict
"""
class Assistant:
    # Properties
    client = None
    name = None
    instructions = None
    tool_set = []
    user_defined_functions = None
    model = None
    model_parameters = None
    vector_store = None
    intance = None
    thread = None

    # Constructor
    """
    Constructor for the Assistant class.
    
    Parameters
        client (OpenAI): The OpenAI client object
        assistant_name (str): The name of the assistant
        instruction_prompt (str): The assistant's context prompt
        tool_set (list): A list of tool dictionaries
            Defaults to a list containing just the file_search tool
        function_dictionary (dict): A dictionary of user defined functions
            Defaults to an empty dictionary
        model (str): The model to use for the assistant
            Defaults to "gpt-3.5-turbo-0125"
        model_parameters (dict): The parameters for the model
            Defaults to {temperature: 1.0, top_p: 1.0}
    """
    def __init__(
            self, client:OpenAI, assistant_name:str, instruction_prompt:str, tool_set:list|None=None,
            function_dictionary:dict|None=None, model:str|None=None, model_parameters:dict|None=None
        ):
        # Hande defaults
        if model_parameters is None:
            model_parameters = DEFAULT_MODEL_PARAMETERS
        if model is None:
            model = DEFAULT_MODEL
        if function_dictionary is None:
            function_dictionary = {}
        if tool_set is None:
            tool_set = [
                {
                    "type": "file_search"
                }
            ]

        # Verify file_search tool is present
        tool_set = self.__Verify_File_Search_Tool(tool_set)
        
        # Set properties
        self.client = client
        self.name = assistant_name
        self.instructions = instruction_prompt
        self.tool_set = tool_set
        self.user_defined_functions = function_dictionary
        self.model = model
        self.model_parameters = model_parameters

        # Create internal vector store
        self.vector_store = Vector_Storage.Vector_Storage(
            openai_client=self.client,
            name=f"{self.name}_Vector_Store",
            life_time=1
        )

        # Create assistant
        self.intance = self.client.beta.assistants.create(
            model=self.model,
            name=self.name,
            instructions=self.instructions,
            tools=self.tool_set,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [
                        self.vector_store.Get_Attributes()["id"]
                    ]
                }
            },
            temperature=self.model_parameters["temperature"],
        )

        # Initialize thread
        self.thread = client.beta.threads.create()
    # End of Constructor

    """
    Verifies that the file_search tool is present in the tool set. If not, adds it.

    Parameters
        tool_set (list): A list of tool dictionaries
    
    Returns
        tool_set (list): The updated tool set
    """
    def __Verify_File_Search_Tool(self, tool_set:list) -> list:
        # Variable initialization
        tools_present = {
            'function': 0,
            'file_search': 0,
            'code_interpreter': 0
        }

        # Check for file_search tool
        for tool in tool_set:
            tools_present[tool["type"]] += 1

        # Add file_search tool if not present
        if tools_present["file_search"] == 0:
            tool_set.append({
                "type": "file_search"
            })

        # Return tool set
        return tool_set
    # Function End

    """
    Deletes the assistant. Call this method once you are done using the assistant.

    Parameters
        Clear_Vector_Store (bool): A flag to delete the files attached to the internal vector store.
            Defaults to False.

    Returns
        deletion_object.status (bool): The status of the operation
    """
    def Delete_Assistant(self, Clear_Vector_Store:bool|None=None) -> bool:
        # Handle defaults
        if Clear_Vector_Store is None:
            Clear_Vector_Store = False

        # get assistant id
        assistant_id = self.intance.id

        # Delete vector store object
        self.vector_store.Delete_Vector_Store(
            delete_attached=Clear_Vector_Store
        )

        # Delete assistant
        deletion_object = self.client.beta.assistants.delete(
            assistant_id=assistant_id
        )

        # update instance
        self.intance = None

        # return status
        return deletion_object.deleted
    # Function End

    """
    Adds a file to the assistant's internal vector store.

    Parameters
        file_path (str): The path to the file

    Returns
        attachment_status (str): The status of the operation
    """
    def Add_File_To_Vector_Store(self, file_path:str) -> str:
        # Add file to vector store
        attachment_status = self.vector_store.Attach_New_File(file_path)

        # return status
        return attachment_status
    # Function End

    """
    Updates the assistant's tools.

    Parameters
        tool_Set (list): A list of tool dictionaries

    Returns
        (bool): The completions status of the operation
    """
    def Update_Tool_Set(self, tool_set:list[dict]) -> bool:
        try:
            # Update tool set
            updated_assistant = self.client.beta.assistants.update(
                assistant_id=self.intance.id,
                tools=tool_set,
            )

            # update intance
            self.intance = updated_assistant
            self.tool_set = tool_set

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
            Defaults to none.

    Returns
        message (dict): The new message object
    """
    def Send_Message(self, message_content:str, message_attachments:list[dict]|None=None) -> dict:
        # Variable initialization
        message = None

        # Handle defaults
        if message_attachments is None: # Create message without attachments
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message_content
            )
        else: # Create message with attachments
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
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message_content,
                attachments=formatted_message_attachments
            )
        
        return message
    # Function End

    """
    Gets the assistant's message history
    and returns a list of message objects.

    Parameters
        history_length (int): The number of messages to retrieve.
            Defaults to 25.
        debugMode (bool): A flag to return unformatted messages.
            Defaults to False.

    Returns
        history (list): A list of message objects
    """
    def Get_Message_History(self, history_length:int|None=None, debugMode:bool|None=None) -> list:
        # Handle defaults
        if history_length is None:
            history_length = DEFAULT_MESSAGE_HISTORY_LENGTH
        elif history_length < 3:
            # This insures that at least 1 assistant and 1 user message are returned.
            # Sometimes the assistant will send 2 messages in a row.
            history_length = 3
        if debugMode is None:
            debugMode = False

        # get the current run instance of the thread
        local_Run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.intance.id,
            max_prompt_tokens=DEFAULT_MAX_PROMPT_TOKENS
        )

        # check if run is complete
        while local_Run.status != "completed":
            local_Run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=local_Run.id
            )

            # check for pending functions
            if local_Run.status == "requires_action":
                pending_Functions = local_Run.required_action.submit_tool_outputs.tool_calls

                # handle function calls
                self.__Handle_Function_Calls(self.client, local_Run, pending_Functions)

        # get history
        message_History = self.client.beta.threads.messages.list(
            thread_id=self.thread.id,
            limit=history_length,
            order="asc"
        ).data

        if debugMode is True:
            # return unformatted history
            return message_History
        else:
            # format history
            message_History_F = []
            for message in message_History:
                if message.role == "assistant":
                    message_History_F.append(f"{self.name}: {message.content[0].text.value}")
                else:
                    message_History_F.append(f"User: {message.content[0].text.value}")
            return message_History_F
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
            for functionName in self.user_defined_functions.keys():
                if functionName == functionDetails["name"]:
                    try:
                        # Import libray
                        exec(self.user_defined_functions[functionName][0])

                        # Build funciton call
                        function_call_string = self.user_defined_functions[functionName][1] + "("
                        for i in range(self.user_defined_functions[functionName][2]):
                            if i != 0:
                                function_call_string = function_call_string + ", "
                            function_call_string = function_call_string + "\'" + args[i] + "\'"
                        function_call_string = function_call_string + ")"

                        # Execute function
                        returnObject = eval(function_call_string)
                    except Exception as e:
                        print(e)
                        # Return fail case
                        returnObject = self.user_defined_functions[functionName][3]
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

    """
    Gets the assistant's attributes.

    Parameters
        None

    Returns
        attributes (dict): The assistant's attributes
    """
    def Get_Attributes(self) -> dict:
        attributes = {
            "id": self.intance.id,
            'creation time': self.intance.created_at,
            "name": self.name,
            "instructions": self.instructions,
            "tool_set": self.tool_set,
            "user_defined_functions": self.user_defined_functions,
            "model": self.model,
            "model_parameters": self.model_parameters,
            "vector_store": self.vector_store.Get_Attributes(),
            "thread id": self.thread.id
        }

        return attributes
    # Function End

# Class End