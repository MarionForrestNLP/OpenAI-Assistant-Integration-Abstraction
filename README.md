# **OpenAI Assistant Class Integration**

## Goal

This project was initialized to make the [OpenAI](https://platform.openai.com/docs/api-reference/introduction) assistant easier to integrate into your own projects.

## Assistant Class

This class is used to facilitate all interactions with the OpenAI [assistant](https://platform.openai.com/docs/assistants/overview/agents). To construct an assistant you must pass in your OpenAI client instance, a name for the assistant, an instruction prompt, a tool set and their resources. All other parameters are optional.

### Properties

- **Client**: The OpenAI connection intance used to access the assistant and other APIs.
- **Model**: The OpenAI AI model utilized by the assistant. gpt4, 3.5, etc.
- **Name**: The name of the assistant as is displayed on OpenAI assistants dashboard.
- **Instructions**: The prompt used to set up the assistant's initial context and behavior.
- **Tool Set**: The list of tools used by the assistant. file search, code interpreter, and function calling.
- **Tool Resources**: The dictionary containing the id's of vector stores used by different tools.
- **User Defined Functions**: The dictionary containing information about user defined functions. How this dictionary is used is explained further down. Defaults to an empty dictionary.
- **Model Parameters**: The dictionary containing the assistant's model response parameters. Currently includes temperature and top P. Defaults to a temperature of 1 and a top_p of 1.
- **Intance**: This is the instance of the Assistant that our chat bot is tied to and actively using.
- **Thread**: This is the object in which user and assistant interactions are stored.

### Methods

- **Add File to Vector Store**: This method adds a file to the assistant's internal vector store. It takes a file path as input, opens the file, creates a [file object](https://platform.openai.com/docs/api-reference/vector-stores-files/file-object) using the OpenAI client, and then adds the file to the assistant's internal vector store. The method returns the status of the vector file.

- **Update Tool Set**: This method updates the tool set and tool resources used by the assistant. It takes a list of tool dictionaries and a dictionary of tool resources as input. It updates the assistant instance, tool set, and tool resources properties. The method returns a boolean indicating whether the update was successful or not.

- **Delete Assistant**: This method deletes the assistant instance. It gets the assistant ID, [deletes the assistant](https://platform.openai.com/docs/api-reference/assistants/deleteAssistant) using the OpenAI client, and then updates the assistant instance property to None. The method returns a boolean indicating whether the deletion was successful or not.

- **Send Message**: This method creates a [message object](https://platform.openai.com/docs/api-reference/messages/object) and inserts it into the assistant's thread. The message object is then returned. [Attachments](https://platform.openai.com/docs/api-reference/messages/createMessage#messages-createmessage-attachments) can be added to a message and will inserted into the thread along side the message's content.

- **Get Message History**: This method returns the entire chat log up to a maximum of 25 messages. This method also checks for when the assistant is attempting to call [developer defined functions](https://platform.openai.com/docs/assistants/tools/function-calling/function-calling-beta) and calls the `Handle_Function_Calls` function defined earlier within **Assistant_Hander.py**.

- **Print Characteristics**: Prints a string containing some key characteristics of the assistant. These characteristics are the assistant's id, name, creation time, description, instructions, metadata, tools, tool resources, repsonse format, model, temperature, and top p (not in that order).

## User Defined Functions

The OpenAI assistant supports user defined [function calling](https://platform.openai.com/docs/assistants/tools/function-calling/function-calling-beta), which allows you to describe functions to the assistant and have it intelligently return the functions that need to be called along with their arguments. For this integration of the assistant, there are two steps required to get the assistant to effectively utilize your functions.

### Step 1: Tool Set Definition

Within the tool set list, you must define and describe your function. This definition is [passed to the assistant](https://platform.openai.com/docs/assistants/tools/function-calling/step-1-define-functions) for it to identify when certain functions should be called. It is recommended to be as detailed as possible in the `description` fields. Include when the function should be called, what the function returns, how to use the return, and what to do when the assistant doesn't know all the required parameters.

#### Function Tool Example

    {
        "type":"function,
        "function": {
            "name": "Get_Current_Temperature",
            "description": "Get the current temperature for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["Celsius", "Fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the user's location."
                    }
                }
            },
            "required": ["location", "unit"]
        }
    }

### Step 2: User Defined Function Dictionary

Within the constructor, after the tool resources, you must pass in a dictionary that details that format of the call of the function. This is used to within the assistant class to actually call the functions the OpenAI assistant is requesting. Each key:value pair needs to be of the following format. The key should be the name of the function as it appears in the tool set definition. The value is a tuple of 4 elements. Element 1 is a string representing how the funcition's library should be imported. Element 2 is string representing how the function should be called (exlcluding the parentheses). Element 3 is an integer representing the number of parameters the function takes. Element 4 is a string representing what the function returns as a failed case or when given the wrong input (This is passed to the assistant in the event that the function fails to execute).

#### Function Dictionary Example

    {
        "Get_Current_Temperature" : (
            "Import My_Functions",
            "My_Functions.Get_Current_Temperature",
            2,
            "None"
        )
    }

***More documentation coming soon...***
