# **OpenAI Assistant Integration Abstraction**

## Goal

This project was initialized to make the [OpenAI](https://platform.openai.com/docs/api-reference/introduction) API easier to integrate into your own projects. With an emphasis on abstracting the [assistants api](https://platform.openai.com/docs/api-reference/assistants).

## Planned Features and Changes

- Rewrite the [Get_Message_History](#assistant-methods) to be more efficient.

## Table of Contents

- [Assistant Class](#assistant-class)
- [Vector Store Class](#vector-store-class)
- [User Defined Functions](#user-defined-functions)

## Assistant Class

This class is designed to abstract interactions with the OpenAI [Assistant](https://platform.openai.com/docs/assistants/overview/agents). This implementation of the Assistant API does not support the [Code Interpreter](https://platform.openai.com/docs/assistants/tools/code-interpreter/code-interpreter-beta) tool. However, this implementation does have the [File Search](https://platform.openai.com/docs/assistants/tools/file-search/file-search-beta) tool built in and the [Function Calling](https://platform.openai.com/docs/assistants/tools/function-calling/function-calling-beta) tool can be added as an optional feature.

### Assistant Properties

- **Client**: The OpenAI connection intance used to access the assistant and other APIs.
- **Name**: The name of the assistant as is displayed on OpenAI assistants dashboard.
- **Instructions**: The context prompt used to set up the assistant's initial behavior. Be concise and clear in your instructions to the assistant. This prompt is included in the **prompt tokens** count, thus it is recommended you keep it as short as possible.
- **Tool Set**: The list of tools used by the assistant. file search, code interpreter, and function calling.
- **User Defined Functions**: The dictionary containing information about user defined functions. How this dictionary is used is explained under [User Defined Functions](#user-defined-functions).
- **Model**: The OpenAI AI model utilized by the assistant. gpt4, 3.5, etc.
- **Model Parameters**: The dictionary containing the assistant's model response parameters. Currently includes temperature and top P.
- **Max Prompt Tokens**: The maximum number of tokens allowed in a prompt by a user.
- **Max Completion Tokens**: The maximum number of tokens allowed in a response from the assistant.
- **Vector Store**: This is the internally referenced vector store used by the assistant. This is an instance of the [Vector Store class](#vector-store-class).
- **Intance**: This is the instance of the Assistant that our chat bot is tied to and actively using.
- **Thread**: This is the object in which user and assistant interactions are stored.

### Assistant Constructor

The constructor takes in the OpenAI client, the name of the assistant as a string, the instruction prompt as a string, the tool set as a list, a function dicitonary, the open ai model to implement as a string, and the model parameters as a dictionary. It then creates an assistant object using the OpenAI client and stores it in the instance property. The function dictionary is optional and will default to an empty dicitonary. The model string is optional and will default to `"gpt-3.5-turbo-0125"`. The model parameter dictionary is optional and will default to the following.

    model_parameters = {
        "temperature": 1.0,
        "top_p": 1.0
    }

The max prompt tokens and max completion tokens parameters are bot integers and will both be set to 5,000 by default.

### Assistant Methods

There are several methods designed to uphold the internal integrity of the class and are not intended to be called directly into your implementation. Those methods are not be listed below. The following are methods designed to be used in your implementations of this class.

- **Delete Assistant**: This method deletes the assistant instance. It gets the assistant ID, [deletes the assistant](https://platform.openai.com/docs/api-reference/assistants/deleteAssistant) using the OpenAI client, and then updates the assistant instance property to None. The method returns a boolean indicating whether the deletion was successful or not.

- **Attach File**: Takes in a list of file path strings and passes the repective file paths to the [attach new file](#vector-store-methods) method of the assistant's internal [vector store](#vector-store-class). Returns False if any of the files were not added successfully or if no file paths were provided.

- **Update Tool Set**: This method updates the tool set used by the assistant. It takes a list of tool dictionaries. It updates the assistant instance and tool set. The method returns a boolean indicating whether the update was successful or not.

- **Send Message**: This is an *asynchronous* method that creates a [message object](https://platform.openai.com/docs/api-reference/messages/object) and inserts it into the assistant's thread. The message object is then returned.

- **Get Message History**: This is an *asynchronous* method that takes in a `history_length` parameter and returns the entire chat log up to a maximum of `history_length` messages. This method also handles the assistant's attempts at calling [developer defined functions](https://platform.openai.com/docs/assistants/tools/function-calling/function-calling-beta). This method prints a loading message to the console while it waits for the assistant to finish its response. When `debugMode` is False or None, the method returns a list of dictionaries of the following format.

        message = {
            "role": "user" or "assistant",
            "text": "the message's text content",
        }

- **Get Attributes**: This method returns a dictionary containing the assistant's attributes. The dictionary contains the assistant's ID, creation time (*in seconds*), name, instructions, tool set, user defined functions, model, model parameters, vector store, and thread id.

- **Get Vector Store**: This method returns the assistant's internal [vector store](#vector-store-class).

## Vector Store Class

This class is designed to abstract and simplify interactions with vector stores. The main goal of this class was to remove reducancies within the assistant class.

### Vector Store Properties

- Client: The Open AI client used to access the vector store and other APIs.
- Name: A string representing the name of the vector store.
- Days Until Expiration: An integer representing the number of 24 hour days until the vector store expires.
- Instance: The vector store object being abstracted.

### Vector Store Constructor

The constructor takes in the OpenAI client, the name of the vector store, and the number of days until the vector store expires. It then creates a vector store object using the OpenAI client and stores it in the instance property. The name and days until expiration properties are optional and will default to `"Vector_Storage"` and `1` respectively.

### Vector Store Methods

- **Retrieve Vector Store**: This method allows you to replace the vector store created at initialization with a pre-existing vector store. It takes in the ID  of the vector store you want to retrieve. This method deletes the old instance of the the vector store and returns the retrieved instance.

- **Delete Vector Store**: This method deletes the vector store instance. It gets the vector store ID, [deletes the vector store](https://platform.openai.com/docs/api-reference/vector-stores/delete) using the OpenAI client, and then updates the vector store instance property to None. The method returns a boolean indicating whether the deletion was successful or not.

- **Modify Vector Store**: This method modifies the vector store instance. It takes in string representing the new name of the vector store and an integer representing the new number of days until the vector store expires. It then updates the vector store instance property with the new name and days until expiration. The method returns the modified instance.

- **Get Attributes**: This method returns a dictionary containing the vector store's attributes. The dictionary contains the vector store's ID, name, status, creation time (*in seconds*), days until expiration, file count, memory usage (*in bytes*).

- **Attach Existing File**: This method attaches an existing file to the vector store. It takes in the ID of the file you want to attach. It then creates a [vector store file object](https://platform.openai.com/docs/api-reference/vector-stores-files/file-object) using the OpenAI client to attach the file to the vector store. The method returns the status of the file attachment.

- **Attach New File**: This method attaches a new file to the vector store. It takes in the path of the file you want to attach and the purpose of the file as an optional parameter (defaults to "assistant"). It then creates a [file object](https://platform.openai.com/docs/api-reference/files/object) using the OpenAI client then passes the file's id to the `Attach_Existing_File` method to attach the file to the vector store. The method returns the status of the file attachment.
  - Valid purposes are "assistants", "vision", "fine-tuning", and "batch".

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

In this example, the library from which our function `Get_Current_Temperature` is imported is `Weather_Functions`. The function is called by `Weather_Functions.Get_Current_Temperature`. Recall that the function takes 2 parameters, `location` and `unit`. And in this case the function returns `None` when the function fails to execute.

    {
        "Get_Current_Temperature" : (
            "Import Weather_Functions",
            "Weather_Functions.Get_Current_Temperature",
            2,
            "None"
        )
    }

***More documentation coming soon...***
