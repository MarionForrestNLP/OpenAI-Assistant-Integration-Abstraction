# Imports
import os
import time
import Vector_Storage
from openai import AssistantEventHandler, OpenAI
from openai.types import beta as Beta_Types
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Message, Text, TextDelta, Run
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta
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
    This class is designed to abstract interactions with the OpenAI Assistant

    Properties
        client (OpenAI): The OpenAI client instance
        name (str): The name of the assistant
        instructions (str): The assistant's context prompt
        tool_set (list): A list of tool dictionaries
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
        Get_Response(event_handler:AssistantEventHandler) -> None
        Get_Attributes() -> dict
        Get_Vector_Store() -> Vector_Storage.Vector_Storage
    """

    # Properties
    client:OpenAI
    name:str|None = ""
    instructions:str|None = ""
    tool_set:list|None = []
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
            model:str|None=None, model_parameters:dict|None=None,
            max_prompt_tokens:int|None=None, max_completion_tokens:int|None=None
        ):
        """
        This class is designed to abstract interactions with the OpenAI Assistant.
        
        Parameters
            client (OpenAI): The OpenAI client object
            assistant_name (str): The name of the assistant
            instruction_prompt (str): The assistant's context prompt
            tool_set (list): A list of tool dictionaries. | OPTIONAL
            model (str): The model to use for the assistant. | OPTIONAL | DEFAULT: "gpt-3.5-turbo-0125"
            model_parameters (dict): The parameters for the model. | OPTIONAL | DEFAULT: {temperature: 1.0, top_p: 1.0}
            max_prompt_tokens (int): The maximum number of prompt tokens. | OPTIONAL | DEFAULT: 10000
            max_completion_tokens (int): The maximum number of completion tokens. | OPTIONAL | DEFAULT: 10000
        """

        # Hande defaults
        if (model_parameters is None) or (len(model_parameters.keys()) == 0):
            model_parameters = DEFAULT_MODEL_PARAMETERS
        if model is None:
            model = DEFAULT_MODEL
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
            Clear_Vector_Store (bool): A flag to delete the files attached to the internal vector store. | OPTIONAL

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

    def Attach_Files(self, file_paths:list[str]|None) -> list[str]:
        """
        Takes in a list of file path strings and adds the repective files to the assistant's internal vector store.
        Returns a list of file IDs.

        Parameters
            file_paths (list): A list of file paths strings

        Returns
            returnBool (bool): A boolean indicating if all files were added successfully
        """
        # Variable initialization
        id_list = []

        # Check if file paths are provided
        if (file_paths is not None) and (len(file_paths) > 0):
            # Iterate through file paths
            for file_Path in file_paths:
                # Check if file path exists
                if os.path.exists(file_Path) == True:
                    # Send to vector store
                    file_ID = self.vector_store.Attach_New_File(file_path=file_Path)

                    # Add file ID to list
                    id_list.append(file_ID)

                # File path does not exist
                else:
                    id_list.append(None)
            # Loop End
                
            # return status
            return id_list
        
        # No file paths provided
        else:
            return id_list
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
    
    def __Create_Message(self, role:str, content:str, attachment_id:str|None=None) -> Message:
        """
        Internal Method to create a new message in the assistant's thread.

        Parameters
            role (str): The role of the originator of the message
            content (str): The content of the message
            attachment_id (str): The file ID of the attachment | OPTIONAL

        Returns
            message (Message): The new message object
        """
        return self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=content,
            attachments=[{
                "file_id": attachment_id,
                "tools": [{"type": "file_search"}]
            }] if attachment_id is not None else None
        )

    def Send_Message(self, message_content:str, attachment_path:str|None=None, attachment_file_id:str|None=None) -> Message:
        """
        Adds a new message to the assistant's thread
        and returns the new message object.

        Parameters
            message_content (str): The text content of the message
            attachment_path (str): The path to the attachment | OPTIONAL
            attachment_file_id (str): The file ID of the attachment | OPTIONAL
        Returns
            message (Message): The new message object
        """        
        # Variable initialization
        message = None

        # Attachment ID
        if attachment_file_id is not None:
            # Send message
            message = self.__Create_Message(
                role="user",
                content=message_content,
                attachment_id=attachment_file_id
            )

        # Attachment Path
        elif attachment_path is not None:
            # Attach file to vector store
            file_ID = self.vector_store.Attach_New_File(file_path=attachment_path)

            # Send message
            message = self.__Create_Message(
                role="user",
                content=message_content,
                attachment_id=file_ID
            )

        # No attachment
        else:
            # Send message
            message = self.__Create_Message(
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

    def Get_Response(self, event_handler:AssistantEventHandler|None=None) -> None:
        """ 
        Streams the assistant's response to the console (or to wherever the event_handler class defines).

        Parameters
            event_handler (AssistantEventHandler): The event handler class to use. | OPTIONAL

        Returns
            None
        """
        # Handle defaults
        if event_handler is None:
            event_handler = Assistant_Event_Handler

        # Run stream
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.intance.id,
            event_handler=event_handler(client=self.client)
        ) as stream:
            stream.until_done()
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

class Assistant_Event_Handler(AssistantEventHandler):
    """
    A class that handles streaming actions taken by the assistant.

    Properties
        client (OpenAI)

    Overridden Methods
        on_event(event: AssistantStreamEvent)
        on_text_created(text: Text)
        on_text_delta(delta: TextDelta, snapshot: Text)
        on_text_done(text: Text)
        on_message_done(message: Message)

    Methods
        Handle_Required_Actions(data: Run, run_id: str) -> None
        Submit_Tool_Outputs(tool_outputs: list[dict], run_id: str) -> None
    """
    
    @override
    def __init__(self, client:OpenAI) -> None:
        super().__init__()
        self.client = client
    # Function End    

    # \/ \/ Event Handlers \/ \/
    @override
    def on_event(self, event:AssistantStreamEvent) -> None:
        # Identify user function calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.Handle_Required_Actions(event.data, run_id)
    # Function End

    # \/ \/ Text Generation \/ \/
    @override
    def on_text_created(self, text: Text) -> None:
        print(f"\n", end="", flush=True)
    # Function End    

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        print(delta.value, end="", flush=True)
    # Function End    

    @override   
    def on_text_done(self, text: Text) -> None:
        print("", end="\n", flush=True)
    # Function End    

    # \/ \/ Tool Handling \/ \/
    def Handle_Required_Actions(self, data: Run, run_id: str) -> None:
        """
        Left Empty for users to override with their custom actions.
        """
        return None
    # Function End

    @override
    def on_tool_call_created(self, tool_call: ToolCall) -> None:
        super().on_tool_call_created(tool_call)

    @override
    def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall) -> None:
        super().on_tool_call_delta(delta, snapshot)
    
    def Submit_Tool_Outputs(self, tool_outputs: list[dict], run_id: str) -> None:
        """
        [DO NOT OVERRIDE]

        Submits tool outputs to the assistant.
        Pass in a list of tool outputs to submit them to the assistant.

        Parameters
            tool_outputs (list[dict]): A list of tool output dictionaries
            run_id (str): The ID of the run to submit the tool outputs to

        Returns
            None
        """

        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=self.__class__(client=self.client)
        ) as stream:
            stream.until_done()
    # Function End

    # \/ \/ Message Handling \/ \/
    @override
    def on_message_done(self, message: Message) -> None:
        # print a citation to any files searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        if (len(citations) > 0):
            print(f"{''.join(citations)}", end="\n", flush=True)
    # Function End    
# Class End