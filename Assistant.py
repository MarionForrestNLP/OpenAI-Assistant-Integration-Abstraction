from openai import OpenAI
import Local_Keys

# Set up functions

def Assistant_Context() -> str:
    context = f"""You are NLPete, the digital spokesperson for the company NLP Logix.
Your job is assist potential customers with their questions and concerns.
Try to keep your responses relavent to the company and its operations. Try to limit your responses to 200 characters.
Utilize the attached fact sheets to give explicit answers or say 'I don't know at this time. But I will have someone get in connect with you soon. Please give me your email.' if you can not find the answer.
If a client wants to get in contact with the company, give them our contact information and ask for their company name and for an email to contact them with.
When the client gives you a greeting, say something along the lines of "Hello, I am NLPete. How can I assist you today."
"""
    return context

def Get_Assistant_Tools() -> list:
    assistantTools = [
        {
            "type": "file_search"
        },
        {
            "type": "function",
            "function": {
                "name": "Record_Client_Email",
                "description": "Records the client's email so that they may be contacted at a later time. Call this function when the client has given you their email and company name. Returns True if successful, False if not.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "clientEmail": {
                            "type": "string",
                            "description": "The client's email"
                        },
                        "clientCompanyName": {
                            "type": "string",
                            "description": "The client's company name"
                        }
                    },
                    "required": ["textBody"],
                }
            }
        }
    ]
    return assistantTools

def Get_Tool_Resources(client:OpenAI) -> dict:
    try:
        # Retrieve vector store
        vectorStore = client.beta.vector_stores.retrieve(
            vector_store_id=Local_Keys.Get_Vector_Store_ID()
        )
    except:
        # Upload info files
        filePaths = [r"./NLP_Logix_Company_Fact_Sheet.docx"]
        fileIDs = []
        for filePath in filePaths:
            fileObject = client.files.create(
                file=open(filePath, "rb"),
                purpose="assistants"
            )

            fileIDs.append(fileObject.id)
        
        # Create vector store for fact sheets
        vectorStore = client.beta.vector_stores.create(
            name="Company_Fact_Sheets",
            file_ids=fileIDs,
            expires_after={
                "anchor": "last_active_at",
                "days": 1
            }
        )

        # Save vector store id
        Local_Keys.Set_Vector_Store_ID(vectorStore.id)

    # Create tool resources
    toolResources = {
        "file_search": {
            "vector_store_ids": [vectorStore.id]
        }
    }

    # return
    return toolResources

class Assistant:    

    # Constructor
    def __init__(self, client:OpenAI):
        self.client = client

        try:
            # Retrieve assistant
            assistant = Update_Assistant(self)

    # Update assistant
    def Update_Assistant(self):
        # Get assistant
        assistant = self.client.beta.assistants.retrieve(
            assistant_id=Local_Keys.Get_Assistant_ID(),
        )

        # Update assistant
        assistant = self.client.beta.assistants.update(
            assistant_id=Local_Keys.Get_Assistant_ID(),
            instructions=Assistant_Context(),
            tools=Get_Assistant_Tools(),
            tool_resources=Get_Tool_Resources(self.client)
        )

        # return assistant
        return assistant

