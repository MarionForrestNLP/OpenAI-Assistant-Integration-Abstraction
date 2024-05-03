# Imports
import Assistant_Handler as AH
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
def FormatMessage(messageObject, debugMode:bool=False) -> str:
    if debugMode: # Debug Mode
        textValue = messageObject.content[0]
    else: # Normal Mode
        textValue = messageObject.content[0].text.value
    
    # Remaining execution
    textRole = messageObject.role

    if textRole == "assistant":
        return f"NLPete: {textValue}\n"
    else:
        return f"User: {textValue}\n"

"""
Handles the chat experience with the assistant

Parameters
    assistant (Assistant_Handler.Assistant): An assistant object

Returns
    None
"""
def Chat(assistant:AH.Assistant) -> None:
    while True:
        # get user input
        userInput = str(input("User: "))
        if len(userInput.split(" ")) > 100 or len(userInput > 1000):
            print("Your message is too long. Please try to shorten it.")
            time.sleep(3)
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

    # Get assistant
    assistant = AH.Assistant(client)

    # Start chat
    Chat(assistant)

if __name__ == "__main__":
    Main()