# Import the Assistant Class and relevant libraries
import Assistant
import asyncio
from openai import OpenAI

# Create the main function
async def Main():
    # Create an instance of the OpenAI class
    import Local_Keys
    client = OpenAI(
        api_key=Local_Keys.Here()
    )

    # Create an instance of the Assistant class
    asssistant = Assistant.Assistant(
        # Pass in the OpenAI client || REQUIRED
        client=client,
        
        # Pass in a name for the assistant || REQUIRED
        assistant_name="Example Assistant",
        
        # Pass in an instruction prompt || REQUIRED
        instruction_prompt="You are a simple chat bot",
        
        # Pass in a list of tools. If left empty, the "file_search" tool is automatically added || OPTIONAL
        tool_set=[],
        
        # Pass in a dictionary of user defined functions || OPTIONAL
        function_dictionary={},
        
        # Pass in the model name. If left empty, "gpt-3.5-turbo-0125" will be used || OPTIONAL
        model="gpt-3.5-turbo-0125",
        
        # Pass in a dictionary of model parameters. If left empty, default parameters of {temperature: 1.0, top_p: 1.0} will be used || OPTIONAL
        model_parameters={},
        
        # Pass in the maximum number of prompt and completion tokens this assistant can use. If left empty, 10,000 will be used. OpenAI recommends 20,000 || OPTIONAL
        max_prompt_tokens=None,
        max_completion_tokens=None
    )

    # Attach a file to the assistant
    asssistant.Attach_File(
        # Pass in a list of file paths || REQUIRED
        file_paths=["YOUR_FILE_PATH"]
    )

    # Converate with the assistant
    while True:
        # Take in user input
        user_input = input("User: ")

        # Escape clause
        if user_input == "exit":
            break
        else:
            # Send the user input to the assistant | This method is asynchronous and must be awaited
            await asssistant.Send_Message(
                message_content=user_input
            )

        # Get the assistant's response | This method is asynchronous and must be awaited
        assistant_response = await asssistant.Get_Message_History() # Returns a list of both the assistant's and user's messages

        # Print the assistant's response
        print("\nAssistant: " + assistant_response[-1]["text"] + "\n") # Reverse index to get the assistant's response
    # Loop End

    # Delete the assistant once all activities have been completed
    asssistant.Delete_Assistant(
        clear_vector_store=True # I recommend setting this parameter to True to save on storage costs
    )
# Main End

# Run the main function
asyncio.run(Main())
