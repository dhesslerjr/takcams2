import streamlit as st
import os, random
import requests
import groq
import sys
from dotenv import load_dotenv
import re
from pathlib import Path
import tempfile
import takcams_ai

print("Current working directory:", os.getcwd())
print(".env file exists:", os.path.exists('.env'))
load_dotenv(verbose=True)
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ API key not found. Please check your .env file.")
    st.stop()

class TextDatabase:
    """
    A class to manage text-based databases for storing and searching information.

    This class provides functionality to create, update, and search within a text file,
    which serves as a simple database for the PythiaAI-Lab application.
    """

    def __init__(self, aname, content, ftype):
        """
        Initialize the TextDatabase with a given filename.

        Args:
            filename (str): The full file path of the file to use as the database.
            ftype (str): procedure.json|profile|pre-existing|guidelines|knowledgebase
        """
        self.name=aname
        self.ftype=ftype
        self.content = content

        st.info(f"created database: {self.name} of type {self.ftype} with content {self.content}")

    def add_document(self, text):
        """
        Add a new document (text) to the database.

        Args:
            text (str): The text to be added to the database.
        """
        self.content += f"\n{text}"
        self.save()

    def save(self):
        """
        Save the current content of the database to the file.
        """
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(self.content)

    def search(self, query, n_results=1):
        """
        Search the database for content matching the given query.

        Args:
            query (str): The search query.
            n_results (int): The number of results to return.

        Returns:
            list: A list of relevant paragraphs from the database.
        """
        paragraphs = self.content.split('\n\n')
        relevant_paragraphs = [p for p in paragraphs if query.lower() in p.lower()]
        return relevant_paragraphs[:n_results]



class ContextStore:
    def __init__(self):
        self.contexts = []
    
    def add_context(self,file,ftype):
            dbname=os.path.basename(file.name).replace('"','')
            content=file.read()
            self.contexts.append(TextDatabase(dbname,content,ftype))



    

def main():
    """
    The main function that sets up the Streamlit UI and manages the application flow.
    """
    st.title("TaKCaMS v2")
    
    if 'ContextStore' not in st.session_state:
        st.session_state.ContextStore = ContextStore()
        st.session_state.databases_created = False
        st.session_state.takcams = takcams_ai.TakCamsAI(groq_api_key)

    if not st.session_state.databases_created:
        st.header("Database Creation")

        preexisting = st.file_uploader("Upload pre-existing knowledge documents", type=['txt'], accept_multiple_files=True)


        #buf = st.text_area("Enter guideline documents by file path (one per line)", help="Optional")
        #guidelines = buf.splitlines(False)

        #userprofile = st.text_input("Enter user profile document by file path", help="Optional")


        if st.button("Create Databases"):
 
            
            if len(preexisting)>0:
                for p in preexisting:
                    st.session_state.ContextStore.add_context(p,'pre-existing')
                st.session_state.databases_created = True
                st.success("Databases created successfully!")
                #if len(guidelines)>0:
                #    for g in guidelines:
                #        st.session_state.ContextStore.add_context(p,'guideline')
                #if len(userprofile)>0:
                #    st.session_state.ContextStore.add_context(userprofile,'profile')

            else:
                st.error("Please upload at least one pre-existing knowledge file.")

    if st.session_state.databases_created:
        st.header("Hints")
        st.info("Your free hint is " + st.session_state.takcams.get_hint())
        st.header("Ask Questions")
        question = st.text_input("Enter your question (or type 'END' to exit)")
        
        if question.lower() == 'end':
            st.info("Thank you for using TaKCaMS v2. Goodbye!")
            st.stop()
        
        if question:
            st.write(st.session_state.takcams.ask_question(question))

            #i=0
            #for a in answers:
                #i=i+1
                #st.info(str(i) + "|" + answers[a].ftype + "|" + answers[a].dbname + "|verified=" + str(answers[a].verified))
                #st.write(a)
            st.info("responses end here")

if __name__ == "__main__":
    main()
