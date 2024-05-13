from openai import OpenAI
import json

class Vector_Storage:
    # Properties
    client = None
    name = ""
    days_until_expiration = 0
    intance = None

    # Constructor
    """
    Constructor for the Vector_Storage class.

    Parameters:
        openai_client (OpenAI): The OpenAI client object.
        name (str): The name of the vector store. Defaults to "Vector_Storage".
        life_time (int): The time in terms of 24 hour days that the vector store will be kept alive. Defaults to 1.
    """
    def __init__(self, openai_client:OpenAI, name:str="Vector_Storage", life_time:int=1):
        # Set properties
        self.client = openai_client
        self.name = name
        self.days_until_expiration = life_time

        # Create the vector store
        self.intance = self.client.beta.vector_stores.create(
            name=self.name,
            expires_after={
                "anchor": "last_active_at",
                "days": self.days_until_expiration
            }
        )
    # End of Constructor

    """
    Retrieves the vector store with the given id and replaces the instance with the retrieved vector store. Returns None if the vector store was not found.

    Parameters:
        vector_store_id (str): The id of the vector store to retrieve.

    Returns:
        self.intance (dict): The retrieved vector store.
    """
    def Retrieve_Vector_Store(self, vector_store_id:str) -> dict:
        # Try to retrieve the vector store
        try:
            # Retrieve the vector store
            retrieved_vector_store = self.client.beta.vector_stores.retrieve(vector_store_id)

            # Replace the instance with the retrieved vector store
            if self.Delete_Vector_Store():
                self.intance = retrieved_vector_store
                self.name = self.intance.name
                self.days_until_expiration = self.intance.expires_after["days"]

                # Return the retrieved vector store
                return self.intance
            else:
                # Return none if the current vector store was not deleted
                return None
        
        except Exception as e:
            # Return none if the vector store was not found
            return None
    # End of Retrieve_Vector_Store

    """
    Deletes the vector store and sets the instance to None.

    Parameters:
        None

    Returns:
        deletion_status.deleted (bool): A boolean value indicating if the vector store was deleted successfully.
    """
    def Delete_Vector_Store(self, delete_attached:bool=False) -> bool:
        # Delete files attached to the vector store if specified
        if delete_attached:
            # Get the files attached to the vector store
            attached_files = self.client.beta.vector_stores.files.list(vector_store_id=self.intance.id, limit=100).data
            for attached_file in attached_files:
                # Delete the attached file
                self.client.files.delete(attached_file.id)
            # Loop End

        # Delete the vector store
        deletion_status = self.client.beta.vector_stores.delete(self.intance.id)

        # Set the instance to None
        self.intance = None

        # Return the deletion status
        return deletion_status.deleted
    # End of Delete_Vector_Store

    """
    Modifies the vector store with the given new name and life time. Returns the modified vector store.

    Parameters:
        new_name (str): The new name of the vector store.
        new_life_time (int): The new life time of the vector store in terms of 24 hour days.

    Returns:
        self.intance (dict): The modified vector store.
    """
    def Modify_Vector_Store(self, new_name:str=None, new_life_time:int=None) -> dict:
        # Set the new name and life time
        if new_name != None:
            self.name = new_name
        if new_life_time != None:
            self.days_until_expiration = new_life_time

        # Modify the vector store
        modified_vector_store = self.client.beta.vector_stores.update(
            vector_store_id=self.intance.id,
            name=self.name,
            expires_after={
                "anchor": "last_active_at",
                "days": self.days_until_expiration
            }
        )

        # Replace the instance with the modified vector store
        self.intance = modified_vector_store

        # Return the modified vector store
        return self.intance
    # End of Modify_Vector_Store


    """
    Returns a dictionary of the vector store's attributes.

    Parameters:
        None

    Returns:
        attributes (dict): A dictionary of the vector store's attributes.
    """
    def Get_Attributes(self) -> dict:
        # Create an attributes dictionary
        attributes = {
            "id": self.intance.id,
            "name": self.name,
            "status": self.intance.status,
            "created at": self.intance.created_at,
            "days until expiration": self.days_until_expiration,
            "file count": self.intance.file_counts.total,
            "memory usage": self.intance.usage_bytes,
        }

        # Return the status
        return attributes
    # End of Get_Attributes

    """
    Attaches a file with the given id to the vector store. Returns the file's status.

    Parameters:
        file_id (str): The id of the file to attach to the vector store.

    Returns:
        vector_store_file.status (str): The status of the file attachment.
    """
    def Attach_Existing_File(self, file_id:str) -> str:
        # Attach the file
        vector_store_file = self.client.beta.vector_stores.files.create_and_poll(
            vector_store_id=self.intance.id,
            file_id=file_id
        )

        # Return the attachment status
        return vector_store_file.status
    # End of Attach_Existing_File

    """
    Attaches a file with the given path to the vector store. Returns the file's status.

    Parameters:
        file_path (str): The path of the file to attach to the vector store.

    Returns:
        attachment_status (str): The status of the file attachment.
    """
    def Attach_New_File(self, file_path:str) -> str:
        # Upload the file
        uploaded_file = self.client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants"
        )

        # Attach the file
        attachment_status = self.Attach_Existing_File(uploaded_file.id)

        # Return the attachment status
        return attachment_status
    # End of Attach_New_File