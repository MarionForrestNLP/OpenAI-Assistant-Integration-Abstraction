# **NLPete Chat Bot**
*Implemented using the [Open AI API](https://platform.openai.com/docs/api-reference/introduction)*

## Goal
This project was initialized by an intern with the goal to replace the text fields on the contact page on the company website with an AI powered chatbot.

## Assistant Class
There is an **Assistant** class declared within the **Assistant_Handler.py** file. This assistant object is used to facilitate all interactions with the chat bot within one place. 
### Properties
- **Client**: The OpenAI connection intance used to access the assistant and other APIs.
- **Model**: The OpenAI AI model utilized by the assistant. gpt4, 3.5, etc.
- **Name**: The name of the assistant as is displayed on OpenAI assistants dashboard.
- **Instructions**: The prompt used to set up the assistant's initial context and behavior.
- **Tool Set**: The list of tools used by the assistant. file search, code interpreter, and function calling.
- **Tool Resources**: The dictionary containing the id's of vector stores used by different tools.
- **Model Parameters**: The dictionary containing the assistant's model response parameters. Currently includes temperature and top P.
- **Intance**: This is the instance of the Assistant that our chat bot is tied to and actively using.
- **Thread**: This is the object in which user and assistant interactions are stored.
### Methods
- **Add File to Vector Store**: This method adds a file to the assistant's internal vector store. It takes a file path as input, opens the file, creates a [file object](https://platform.openai.com/docs/api-reference/vector-stores-files/file-object) using the OpenAI client, and then adds the file to the assistant's internal vector store. The method returns the status of the vector file.
- **Update Tool Set**: This method updates the tool set and tool resources used by the assistant. It takes a list of tool dictionaries and a dictionary of tool resources as input. It updates the assistant instance, tool set, and tool resources properties. The method returns a boolean indicating whether the update was successful or not.
- **Delete Assistant**: This method deletes the assistant instance. It gets the assistant ID, [deletes the assistant](https://platform.openai.com/docs/api-reference/assistants/deleteAssistant) using the OpenAI client, and then updates the assistant instance property to None. The method returns a boolean indicating whether the deletion was successful or not.
- **Send Message**: This method creates a [message object](https://platform.openai.com/docs/api-reference/messages/object) and inserts it into the assistant's thread. The message object is then returned. [Attachments](https://platform.openai.com/docs/api-reference/messages/createMessage#messages-createmessage-attachments) can be added to a message and will inserted into the thread along side the message's content.
- **Get_Message_History**: This method returns the entire chat log up to a maximum of 25 messages. This method also checks for when the assistant is attempting to call [developer defined functions](https://platform.openai.com/docs/assistants/tools/function-calling/function-calling-beta) and calls the `Handle_Function_Calls` function defined earlier within **Assistant_Hander.py**.

***More documentation coming soon...***
