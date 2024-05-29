# Imports
import json
import os
import time
import Vector_Storage
from openai import AssistantEventHandler, OpenAI
from openai.types import beta as Beta_Types
from openai.types.beta.threads import Message, Text, TextDelta
from typing import Callable
from typing_extensions import override

# Constants
DEFAULT_MODEL = "gpt-3.5-turbo-0125"
DEFAULT_MESSAGE_HISTORY_LENGTH = 25
DEFAULT_MAX_PROMPT_TOKENS = 10000 # OpenAI recommends at least 20,000 prompt tokens for best results
DEFAULT_MAX_COMPLETION_TOKENS = 10000
DEFAULT_MODEL_PARAMETERS = {
    "temperature": 1.0,
    "top_p": 1.0
}

# \/ \/ Classes \/ \/
class Assistant:
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
        max_prompt_tokens (int): The maximum number of prompt tokens
        max_completion_tokens (int): The maximum number of completion tokens
        vector_store (Vector_Storage): The internal vector store
        intance (openai.types.beta.Assistant): The OpenAI Assistant instance
        thread (openai.types.beta.Thread): The Assistant Thread instance

    Methods
        Delete_Assistant() -> bool
        Attach_Files(file_paths:list[str]) -> bool
        Update_Tool_Set(tool_set:list) -> bool
        Send_Message(message_content:str, message_attachments:list=[]) -> dict
        Get_Message_History() -> list
        Get_Attributes() -> dict
        Get_Vector_Store() -> Vector_Storage.Vector_Storage
    """

    # Properties
    client:OpenAI
    name:str|None = ""
    instructions:str|None = ""
    tool_set:list|None = []
    user_defined_functions:dict|None = {}
    model:str|None = ""
    model_parameters:dict|None = {}
    max_prompt_tokens:int|None = None
    max_completion_tokens:int|None = None
    vector_store:Vector_Storage.Vector_Storage
    intance:Beta_Types.Assistant
    thread:Beta_Types.Thread

    # Constructor
    def __init__(
            self, client:OpenAI, assistant_name:str, instruction_prompt:str, tool_set:list|None=None,
            function_dictionary:dict|None=None, model:str|None=None, model_parameters:dict|None=None,
            max_prompt_tokens:int|None=None, max_completion_tokens:int|None=None
        ):
        """
        This class is designed to abstract interactions with the OpenAI Assistant.
        
        Parameters
            client (OpenAI): The OpenAI client object
            assistant_name (str): The name of the assistant
            instruction_prompt (str): The assistant's context prompt
            tool_set (list): A list of tool dictionaries. Defaults to a list containing just the file_search tool
            function_dictionary (dict): A dictionary of user defined functions. Defaults to an empty dictionary
            model (str): The model to use for the assistant. Defaults to "gpt-3.5-turbo-0125"
            model_parameters (dict): The parameters for the model. Defaults to {temperature: 1.0, top_p: 1.0}
            max_prompt_tokens (int): The maximum number of prompt tokens. Defaults to 5000
            max_completion_tokens (int): The maximum number of completion tokens. Defaults to 5000
        """

        # Hande defaults
        if (model_parameters is None) or (len(model_parameters.keys()) == 0):
            model_parameters = DEFAULT_MODEL_PARAMETERS
        if model is None:
            model = DEFAULT_MODEL
        if (function_dictionary is None) or (len(function_dictionary.keys()) == 0):
            function_dictionary = {}
        if (tool_set is None) or (len(tool_set) == 0):
            tool_set = [
                {
                    "type": "file_search"
                }
            ]
        if max_prompt_tokens is None:
            max_prompt_tokens = DEFAULT_MAX_PROMPT_TOKENS
        if max_completion_tokens is None:
            max_completion_tokens = DEFAULT_MAX_COMPLETION_TOKENS

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
        self.max_prompt_tokens = max_prompt_tokens

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

    def __Verify_File_Search_Tool(self, tool_set:list) -> list:
        """
        Verifies that the file_search tool is present in the tool set. If not, adds it.

        Parameters
            tool_set (list): A list of tool dictionaries
        
        Returns
            tool_set (list): The updated tool set
        """
        
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

    def Delete_Assistant(self, clear_vector_store:bool|None=None) -> bool:
        """
        Deletes the assistant. Call this method once you are done using the assistant.

        Parameters
            Clear_Vector_Store (bool): A flag to delete the files attached to the internal vector store.
                Defaults to False.

        Returns
            deletion_object.status (bool): The status of the operation
        """

        # Handle defaults
        if clear_vector_store is None:
            clear_vector_store = False

        # get assistant id
        assistant_id = self.intance.id

        # Delete vector store object
        self.vector_store.Delete_Vector_Store(
            delete_attached=clear_vector_store
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

    def Attach_Files(self, file_paths:list[str]|None) -> bool:
        """
        Takes in a list of file path strings and adds the repective files to the assistant's internal vector store.
        Returns False if any of the files were not added successfully or if no file paths were provided.

        Parameters
            file_paths (list): A list of file paths strings

        Returns
            returnBool (bool): A boolean indicating if all files were added successfully
        """

        if (file_paths is not None) and (len(file_paths) > 0):
            # Iterate through file paths
            for filePath in file_paths:
                # Check if file path exists
                if os.path.exists(filePath) == True:
                    # Send to vector store
                    attachmentStatus = self.vector_store.Attach_New_File(file_path=filePath)

                    # return status
                    if attachmentStatus == "completed":
                        continue
                    else:
                        return False
                
                # Non-existent file path
                else:
                    # return status
                    return False
            # Loop End
                
            # return status
            return True
        
        # No file paths provided
        else:
            return False
    # Function End

    def Update_Tool_Set(self, tool_set:list[dict]) -> bool:
        """
        Updates the assistant's tools.

        Parameters
            tool_Set (list): A list of tool dictionaries

        Returns
            (bool): The completions status of the operation
        """

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
    
    def Send_Message(self, message_content:str) -> dict:
        """
        Adds a new message to the assistant's thread
        and returns the new message object.

        Parameters
            message_content (str): The text content of the message
        Returns
            message (dict): The new message object
        """

        # Send message
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message_content
        )
        
        # Return message
        return message
    # Function End

    def __Print_Loading_Message(self) -> None:
        """
        Prints a loading message to the console.

        Parameters
            None

        Returns
            None
        """

        # Variable initialization
        outString = f"{self.name} Generating Response"
    
        # Print loading message
        print(outString, end="")
        for __ in range(3):
            for _ in range(3):
                print(".", end="")
                time.sleep(0.1)
            # Loop End

            print("\b"*3 + " "*3 + "\b"*3, end="")
        # Loop End

        # Clear line
        print("\b"*len(outString) + " "*len(outString) + "\b"*len(outString), end="")
    # Function End

    def __Stream_To_Console(self, content:str, position:int) -> None:
        """
        Default message streaming function
        """

        if position <= -1:
            print(f"{self.name}: {content}", end="", flush=True)
        elif position == 0:
            print(content, end="", flush=True)
        elif position >= 1:
            print("", end="\n", flush=True)
    # Function End

    def __Get_Run_Stream(self, print_stream:Callable|None) -> None:
        """
        Under Development, DO NOT USE.
        """

        # Handle defaults
        if print_stream is None:
            print_stream = self.__Stream_To_Console

        # Create an event handler class
        class EventHandler(AssistantEventHandler):
            @override
            def on_text_created(self, text:Text) -> None:
                print_stream(content=f"\nAssistant: ", position=-1)

            @override
            def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
                print_stream(content=delta.value, position=0)

            @override
            def on_text_done(self, text: Text) -> None:
                print_stream(content="", position=1)

            @override
            def on_message_done(self, message: Message) -> None:
                return message.content[0].text.value
        # Class End

        # Run stream
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.intance.id,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()
    # Function End

    def __Process_Run(self) -> bool:
        """
        Processes messages sent to the assistant. Returns a bool indicating if processing was successful.
        """

        # Create a new run instance
        run_instance = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.intance.id,
            max_prompt_tokens=self.max_prompt_tokens,
            max_completion_tokens=self.max_completion_tokens
        )

        # Check run status
        run_status = run_instance.status
        while run_status != "completed":
            # Tool call case
            if run_status == "requires_action":
                # Get tool call details
                toolCallDetails = run_instance.required_action.submit_tool_outputs.tool_calls
                
                # Call functions
                self.__Handle_Function_Calls(
                    client=self.client,
                    runInstance=run_instance,
                    functionObjectList=toolCallDetails
                )

            # Failure case
            elif run_status == "failed":
                return False
            
            # Waiting case
            else:
                # Implement waiting case
                pass

            # Get next run status
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run_instance.id
            ).status
        # Loop End

        # Completion case
        return True
    # Function End

    def __Format_Message(self, message:Message, contentIndex:int) -> dict:
        # Variable initialization
        content_type = message.content[contentIndex].type
        content_value = None

        # Determine content value
        if content_type == "text":
            content_value = message.content[contentIndex].text.value
        elif content_type == "image_file":
            content_value = message.content[contentIndex].image_file.file_id

        # Create formatted message dictionary
        formattedMessage = {
            "creation_time": message.created_at,
            "role": message.role,
            "content": {
                "type": content_type,
                "value": content_value
            }
        }

        # Return formatted message
        return formattedMessage
    # Function End

    def Get_Message_History(self, history_length:int|None=None, debug_mode:bool|None=None) -> list[dict] | list[Message]:
        """
        Returns the entire history of messages from both the assistant and user up to a maximum of history_length messages.
        If debug_mode is set to True, the function will return a list of message objects.
        If debug_mode is set to False, the function will return a list of dictionaries containing limited information from message objects.

        Parameters
            history_length (int): The number of messages to retrieve.
                Defaults to 25.
            debug_mode (bool): A flag to return unformatted messages.
                Defaults to False.

        Returns
            message_History (list[message]): A list of message objects.
                or
            message_History_F (list[dict]): A list of dictionaries containing limited information from message objects.
        """
        # Handle defaults
        if history_length is None:
            history_length = DEFAULT_MESSAGE_HISTORY_LENGTH
        elif history_length < 3:
            # This insures that at least 1 assistant and 1 user message are returned.
            # Sometimes the assistant will send 2 messages in a row.
            history_length = 3
        if debug_mode is None:
            debug_mode = False

        # Process user messages, then check run status
        runStatus = self.__Process_Run()

        # Failure case
        if runStatus is False:
            return [
                {
                    "role": "assistant",
                    "text": "Failed to generate a response."
                }
            ]
        
        # Success case
        else:
            # get history
            message_History = self.client.beta.threads.messages.list(
                thread_id=self.thread.id,
                limit=history_length,
                order="asc"
            ).data

            # Debug case
            if debug_mode is True:
                # return unformatted history
                return message_History
            
            # Normal case
            else:
                # format history
                message_History_F = []
                for message in message_History:
                    for content_index in range(len(message.content)):
                        # Create formatted message
                        formatted_message = self.__Format_Message(
                            message=message,
                            contentIndex=content_index
                        )

                        # Append message to history
                        message_History_F.append(formatted_message)
                    # Loop End
                # Loop End

                # return formatted history
                return message_History_F
    # Function End

    def Get_Latest_Response(self, debug_mode:bool|None=None) -> dict|Message:
        """
        Returns the assistant's response to the most recently sent message.

        Parameters
            debug_mode (bool): A flag to return unformatted messages.
                Defaults to False.

        Returns
            response (str): The assistant's response to the most recently sent message.
        """
        if debug_mode is None:
            debug_mode = False

        # get history
        history = self.Get_Message_History(
            debug_mode=debug_mode
        )

        # Get message
        response = history[-1]

        # return message
        return response
    # Function End

    def __Remove_Escape_Characters(self, message:str) -> str:
        """
        Attempts to remove escape characters from strings used in exec() and eval() calls

        Parameters
            message (str): The message to clean

        Returns
            cleanedMessage (str): The cleaned message
        """

        # Remove single quotes
        cleanedMessage = message.replace("'", "")
    
        # Remove double quotes
        cleanedMessage = message.replace('"', "")

        # Return cleaned message
        return cleanedMessage
    # Function End

    def __Handle_Function_Calls(self, client:OpenAI, runInstance, functionObjectList:list) -> None:
        # Variable initialization
        toolOutputs = []

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
                            function_call_string = function_call_string + "\'" + self.__Remove_Escape_Characters(args[i]) + "\'"
                        function_call_string = function_call_string + ")"

                        # Execute function
                        returnObject = eval(function_call_string)
                        toolOutputs.append({
                            "tool_call_id": functionObjectDict["id"],
                            "output": returnObject
                        })
                    except Exception as e:
                        print(e)
                        # Return fail case
                        returnObject = self.user_defined_functions[functionName][3]
                        toolOutputs.append({
                            "tool_call_id": functionObjectDict["id"],
                            "output": returnObject
                        })
            # Loop End
        # Loop End

        # Update run instance
        updatedRun = client.beta.threads.runs.submit_tool_outputs(
            thread_id=runInstance.thread_id,
            run_id=runInstance.id,
            tool_outputs=toolOutputs
        )

        # Return None
        return None
    # Function End

    
    def Get_Attributes(self) -> dict:
        """
        Gets the assistant's attributes.

        Parameters
            None

        Returns
            attributes (dict): The assistant's attributes
        """

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

    def Get_Vector_Store(self) -> Vector_Storage.Vector_Storage:
        """
        Gets the assistant's vector store.
        
        Parameters
            None
            
        Returns
            vector_store (Vector_Storage): The assistant's vector store
        """

        # Return the vector store
        return self.vector_store
        
    # Function End
# Class End