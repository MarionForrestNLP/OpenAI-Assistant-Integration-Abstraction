# Imports
import Assistant as AST
import Example_Tools
import Local_Keys as LK
import time

from openai import OpenAI
from os import system

# \/ \/ Functions \/ \/

"""
Formats a message object into a string

Parameters
    messageObject (dict): The message object
    debugMode (bool): Whether the message is in debug mode

Returns
    formattedMessage (str): The formatted message
"""
def FormatMessage(messageObject, assistantName:str="Assistant",debugMode:bool=False) -> str:
    if debugMode: # Debug Mode
        textValue = messageObject.content[0]
    else: # Normal Mode
        textValue = messageObject.content[0].text.value
    
    # Remaining execution
    textRole = messageObject.role

    if textRole == "assistant":
        return f"{assistantName}: {textValue}\n"
    else:
        return f"User: {textValue}\n"

"""
Handles the chat experience with the assistant

Parameters
    assistant (Assistant_Handler.Assistant): An assistant object

Returns
    None
"""
def Chat(assistant:AST.Assistant) -> None:
    while True:
        # get user input
        userInput = str(input("User: "))
        if len(userInput.split(" ")) > 100 or len(userInput) > 1000:
            print("Your message is too long. Please try to shorten it.")
            time.sleep(3)
        elif userInput.lower() == "exit":
            assistant.Delete_Assistant()
            break
        else:
            assistant.Send_Message(userInput)

        # Generate response
        print("\nGenerating response...")
        messageList = assistant.Get_Message_History()

        # Clear screen for new messages
        system('cls')

        # Print messages
        for message in messageList:
            # Format message
            formattedMessage = FormatMessage(
                messageObject=message,
                assistantName=assistant.ast_Name,
                debugMode=False
            )

            print(formattedMessage)
        # Loop end
# Function end

"""
Main
"""
def Main() -> None:
    # Clear screen
    system('cls')

    # Get client
    client = OpenAI(api_key=LK.Get_API_Key())

    # Clean up the file store
    Example_Tools.Delete_Old_Vectors(client)

    # Function dictionary
    functionDict = {
        "Record_Client_Email": (
            "import Assistant_Functions",
            "Assistant_Functions.Record_Client_Email",
            2,
            "False"
        )
    }

    # Create assistant
    assistant = AST.Assistant(
        client=client,
        assistant_name="LNPete",
        instruction_prompt=Example_Tools.Get_Assistant_Context(),
        tool_Set=Example_Tools.Get_Assistant_Tools(),
        tool_Resources=Example_Tools.Get_Tool_Resources(client),
        function_Dictionary=functionDict,
        model="gpt-3.5-turbo-0125",
        model_parameters={"temperature": 1.4, "top_p": 1.0}
    )

    # Start chat
    Chat(assistant)

if __name__ == "__main__":
    Main()