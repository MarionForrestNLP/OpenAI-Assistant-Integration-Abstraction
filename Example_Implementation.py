# Import the Assistant Class and relevant libraries
import Assistant
from openai import OpenAI

# Create the main function
def Main():
    # Create an instance of the OpenAI class
    client = OpenAI(
        api_key="YOUR_API_KEY"
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
        
        # Pass in the model name. If left empty, defaults to "gpt-3.5-turbo-0125" || OPTIONAL
        model=None,
        
        # Pass in a dictionary of model parameters. If left empty, default parameters of {temperature: 1.0, top_p: 1.0} will be used || OPTIONAL
        model_parameters={},
        
        # Pass in the maximum number of prompt and completion tokens this assistant can use. If left empty, 10,000 will be used. OpenAI recommends 20,000 || OPTIONAL
        max_prompt_tokens=None,
        max_completion_tokens=None
    )

    # Attach a file to the assistant. This is an optional example, you can delete this line of code if you want.
    asssistant.Attach_Files(
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
            # Send the user input to the assistant
            asssistant.Send_Message(
                message_content=user_input
            )

        # Get the assistant's response
        assistant_response = asssistant.Get_Latest_Response()

        # Print the assistant's response
        print("\nAssistant: " + assistant_response["content"]["value"] + "\n")
    # Loop End

    # Delete the assistant once all activities have been completed
    asssistant.Delete_Assistant(
        clear_vector_store=True # I recommend setting this parameter to True to save on storage costs
    )
# Main End

# Run the main function
if __name__ == "__main__":
    Main()
