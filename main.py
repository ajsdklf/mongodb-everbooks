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
    collection_users = db['users']
    collection_questions = db['questions']
    
    # CRUD Operations Interface
    st.write("## CRUD Operations")
    
    # Read Operation - Users
    st.write("### View Users")
    if st.button("Show All Users"):
        users = list(collection_users.find())  # Convert cursor to list
        if users:
            for user in users:
                st.write(user)
        else:
            st.info("No users found in the database")

    # Read Operation - Questions
    st.write("### View Questions")
    if st.button("Show All Questions"):
        questions = list(collection_questions.find())  # Convert cursor to list
        if questions:
            for question in questions:
                st.write(question)
        else:
            st.info("No questions found in the database")
            
    # Add/Update Questions Operation
    st.write("### Add/Update Questions")
    email_for_questions = st.text_input("Enter email to add/update questions:")
    if email_for_questions:
        user = collection_users.find_one({"email": email_for_questions})
        if user:
            st.write("Current user:", email_for_questions)
            
            # Get existing questions for this user
            existing_doc = collection_questions.find_one({"email": email_for_questions})
            existing_questions = existing_doc.get('questions', []) if existing_doc else []
            
            # Create input fields for existing questions
            new_questions = []
            # Add new question field first
            new_question = st.text_area("Add New Question:", "")
            if new_question.strip():  # Only append if not empty
                new_questions.append(new_question)
            
            # Then add existing questions
            for i, question in enumerate(existing_questions):
                edited_question = st.text_area(f"Question {i+1}:", question)
                new_questions.append(edited_question)
            
            if st.button("Save Questions"):
                question_data = {
                    "email": email_for_questions,
                    "questions": new_questions,
                    "updatedAt": datetime.now()
                }
                
                if existing_doc:
                    # Update existing questions
                    result = collection_questions.update_one(
                        {"email": email_for_questions},
                        {"$set": question_data}
                    )
                    if result.modified_count > 0:
                        st.success(f"Successfully updated questions for: {email_for_questions}")
                    else:
                        st.warning("No changes were made")
                else:
                    # Add new questions
                    collection_questions.insert_one(question_data)
                    st.success(f"Successfully added questions for: {email_for_questions}")
        else:
            st.error(f"No user found with email: {email_for_questions}")
    
    # Update Operation
    st.write("### Update User")
    email_to_update = st.text_input("Enter email of user to update:")
    if email_to_update:
        user = collection_users.find_one({"email": email_to_update})
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
                result = collection_users.update_one(
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
            result = collection_users.delete_one({"email": email_to_delete})
            if result.deleted_count > 0:
                st.success(f"Successfully deleted user with email: {email_to_delete}")
            else:
                st.error(f"No user found with email: {email_to_delete}")
        else:
            st.warning("Please enter an email address")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
