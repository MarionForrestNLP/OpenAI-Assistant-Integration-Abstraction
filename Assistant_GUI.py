# GUI imports
import customtkinter
import tkinter as tk

# Assistant imports
import Assistant as AST
import Assistant_Tools
import Local_Keys as Put_Your_API
from openai import OpenAI

#\/ \/ Functions \/ \/
"""
Closes the main window and deletes the assistant instance.

Parameters:
    None

Returns:
    None
"""
def Event_Window_Close() -> None:
    print("Closing window...")

    # Delete the assistant
    assistant.Delete_Assistant(
        Clear_Vector_Store=True
    )

    # Close the window
    mainWindow.destroy()
# Function End

"""
This function retrieves the user input from the entry field, clears the entry field, 
sends the user input to the assistant using the `Send_Message` method of the `assistant` object, 
retrieves the assistant's response history using the `Get_Message_History` method of the `assistant` object, 
updates the chat log textbox by configuring it to be in a normal state, deleting the existing content, 
and inserting the assistant's response history into the textbox. Finally, the textbox is configured 
to be in a disabled state.

Parameters:
    None
    
Returns:
    None
"""
def Event_Send_Button() -> None:
    # Get user input
    userInput = entryField.get()

    # Clear user input field
    entryField.delete(0, tk.END)

    # Send user input to assistant
    assistant.Send_Message(userInput)

    # Get the assistant's response history
    chatLog = assistant.Get_Message_History()

    # Update the chat log textbox
    textbox.configure(state='normal')
    textbox.delete(1.0, tk.END)
    for message in chatLog:
        textbox.insert(tk.END, message + '\n\n')
    textbox.configure(state='disabled')    
# Function End

"""
Create create and connect to an OpenAI API client
"""
print("Connecting to an assistant...")

# Connect to the OpenAI API
client = OpenAI(api_key=Put_Your_API.Here()) # Put your API key here

# Maintainence
Assistant_Tools.Delete_Old_Vectors(client)

# Create an assistant
assistant = AST.Assistant(
    client=client,
    assistant_name="NLPete",
    instruction_prompt=Assistant_Tools.Get_Assistant_Context(),
    tool_set=Assistant_Tools.Get_Assistant_Tools(),
    function_dictionary=Assistant_Tools.Get_Function_Dictionary(),
    model="gpt-3.5-turbo-0125",
    model_parameters={"temperature": 1.4, "top_p": 1.0}
)

# Add file to assistant's vector store
assistant.Add_File_To_Vector_Store(r"NLP_Logix_Company_Fact_Sheet.docx")

"""
Build a simple GUI for the assistant
"""
print("Building the GUI...")

# Create the window
mainWindow = tk.Tk()
mainWindow.title("Assistant Chat App")
mainWindow.minsize(800, 500)

# Create a frame the chat log
outputFrame = customtkinter.CTkFrame(mainWindow, height=400, fg_color='black')
outputFrame.pack(side=tk.TOP, fill='both', expand=True)

# Create a chat log textbox
textbox = customtkinter.CTkTextbox(outputFrame, width=750, height=300)
textbox.pack(expand=True)
textbox.configure(state='disabled')  # configure textbox to be read-only

# Create a frame for the user input
entryFrame = customtkinter.CTkFrame(mainWindow, width=200, height=100, fg_color='lightgray')
entryFrame.pack(side=tk.BOTTOM, fill='both', expand=True)

# Create the user input textbox
entryField = customtkinter.CTkEntry(entryFrame, placeholder_text='Enter Text Here', width=600, height=50, font=('Arial', 24))
entryField.pack(side=tk.LEFT, expand=True)

# Create a send button
button = customtkinter.CTkButton(entryFrame, text='Send', width=100, height=50, command=Event_Send_Button)
button.pack(side=tk.RIGHT, expand=True)

# Set exit protocol
mainWindow.protocol("WM_DELETE_WINDOW", Event_Window_Close)

"""
Main Loop
"""
print("Debug:")
for key in assistant.Get_Attributes():
    print(f"{key}: {assistant.Get_Attributes()[key]}")

print("Running the GUI...")
mainWindow.mainloop()
