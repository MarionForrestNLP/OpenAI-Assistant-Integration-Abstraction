# **NLPete Chat Bot**
*Implemented using the [Open AI API](https://platform.openai.com/docs/api-reference/introduction)*

## Goal
This project was initialized by an intern with the goal to replace the text fields on the contact page on the company website with an AI powered chatbot.

## Assistant Class
There is an **Assistant** class declared within the **Assistant_Handler.py** file. This assistant object is used to facilitate all interactions with the chat bot within one place. 
### Properties
- **Client**: This is the OpenAI connection intance used to access the assistant and other APIs.
- **Intance**: This is the instance of the Assistant that our chat bot is tied to and actively using.
- **Thread**: This is the object in which user and assistant interactions are stored.
### Methods
- **Send Message**: This method creates a [message object](https://platform.openai.com/docs/api-reference/messages/object) using the `user_Input` parameter as it's content. This message is automatically passed to the assistant's thread at initialization. The message object is then returned to be used by the context that called the method.
    - Attachments can be added to a message, however this functionality has not been implement yet for this project.
- **Get_Message_History**: This method returns the entire chat log up to a maximum of 25 messages. This method also checks for when the assistant is attempting to call [developer defined functions](https://platform.openai.com/docs/assistants/tools/function-calling/function-calling-beta) and calls the `Handle_Function_Calls` function defined earlier within **Assistant_Hander.py**.

***More documentation coming soon...***
