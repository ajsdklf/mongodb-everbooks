import streamlit as st
import sys
import subprocess
import pkg_resources
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from dotenv import load_dotenv
import os
# Debug information section
load_dotenv()

st.set_page_config(page_title="MongoDB CRUD App")

st.write("### System Information")
st.write(f"Python Version: {sys.version}")
st.write(f"Python Path: {sys.executable}")

# Display installed packages
st.write("### Installed Packages")
installed_packages = [pkg.key for pkg in pkg_resources.working_set]
st.write(installed_packages)

# Initialize MongoDB connection outside the button click
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    # Test connection
    client.admin.command('ping')
    st.success("Successfully connected to MongoDB!")
    
    # Initialize database and collection
    db = client['data']
    collection = db['users']
    
    # CRUD Operations Interface
    st.write("## CRUD Operations")
    
    # Read Operation
    st.write("### View users")
    if st.button("Show All Users"):
        users = list(collection.find())  # Convert cursor to list
        if users:
            for user in users:
                st.write(user)
        else:
            st.info("No users found in the database")
    
    # Update Operation
    st.write("### Update User")
    email_to_update = st.text_input("Enter email of user to update:")
    if email_to_update:
        user = collection.find_one({"email": email_to_update})
        if user:
            st.write("Current user information:", user)
            
            # Create input fields for updatable information
            new_email = st.text_input("New Email:", user.get('email', ''))
            new_password = st.text_input("New Password:", user.get('password', ''), type="password")
            new_policy_agreed = st.checkbox("Policy Agreed", user.get('policyAgreed', False))
            new_has_paid = st.checkbox("Has Paid", user.get('hasPaid', False))
            new_memories = st.text_area("Memories:", user.get('memories', ''))
            
            if st.button("Update User"):
                update_data = {
                    "email": new_email,
                    "password": new_password,
                    "policyAgreed": new_policy_agreed,
                    "hasPaid": new_has_paid,
                    "memories": new_memories,
                    "updatedAt": datetime.now()
                }
                result = collection.update_one(
                    {"email": email_to_update},
                    {"$set": update_data}
                )
                if result.modified_count > 0:
                    st.success(f"Successfully updated user with email: {email_to_update}")
                else:
                    st.warning("No changes were made")
        else:
            st.error(f"No user found with email: {email_to_update}")
            
    # Delete Operation
    st.write("### Delete User")
    email_to_delete = st.text_input("Enter email of user to delete:")
    if st.button("Delete User"):
        if email_to_delete:
            result = collection.delete_one({"email": email_to_delete})
            if result.deleted_count > 0:
                st.success(f"Successfully deleted user with email: {email_to_delete}")
            else:
                st.error(f"No user found with email: {email_to_delete}")
        else:
            st.warning("Please enter an email address")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
