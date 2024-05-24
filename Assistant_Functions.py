"""
Imports
"""
from datetime import datetime

"""
Saves a client's email to a CSV file.

Parameters
    clientEmail (str): The client's email
    clientCompanyName (str): The client's company name

Returns
    'True' if successful, 'False' if not
"""
def Record_Client_Email(clientEmail:str, clientCompanyName:str) -> str:
    try:
        # write email and company name to file
        with open('client_emails.csv', 'a') as file:
            file.write(f"{str(datetime.now())},{clientCompanyName},{clientEmail}\n")
        
        # return success
        return 'True'
    
    except:
        return 'False'
# Function End

def Unanswerable_Question(question:str|None) -> str:
    if question is None:
        question = "Type 1 Error"

    question = question.replace("," ," --")

    # Record the unanswerable question
    try:
        with open('unanswerable_questions.csv', 'a') as file:
            file.write(f"{str(datetime.now())},{question}\n")
        return 'True'
    except:
        return 'False'
# Function End