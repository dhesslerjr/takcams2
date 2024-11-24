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
import takcams_storage


print("Current working directory:", os.getcwd())
print(".env file exists:", os.path.exists('.env'))
load_dotenv(verbose=True)
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ API key not found. Please check your .env file.")
    st.stop()

def main():
    """
    The main function that sets up the Streamlit UI and manages the application flow.
    """
    st.title("TaKCaMS v2")
    
    if 'ContextStore' not in st.session_state:
        st.session_state.ContextStore = takcams_storage.ContextStore()
        st.session_state.databases_created = False

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

                #DEBUG
                for c in st.session_state.ContextStore.contexts:
                    st.info(f"database: {c.ftype} | {c.name}")
            else:
                st.error("Please upload at least one pre-existing knowledge file.")

    if st.session_state.databases_created:
        if 'takcams' not in st.session_state:
            st.session_state.takcams = takcams_ai.TakCamsAI(groq_api_key)
            st.session_state.takcams.set_contexts(st.session_state.ContextStore.contexts)

        st.header("Hints")
        st.info("Your free hint is " + st.session_state.takcams.get_hint())
        st.header("Ask Questions")
        question = st.text_input("Enter your question (or type 'END' to exit)")
        
        if question.lower() == 'end':
            st.info("Thank you for using TaKCaMS v2. Goodbye!")
            st.stop()
        
        if question:
            answers=st.session_state.takcams.ask_question(question)

            i=0
            for a in answers:
                i=i+1
                #DEBUG
                #st.write(a)
                verified = "False"
                if(a['verified']==True):
                    verified='Verified'
                else:
                    verified='Unverified'
                st.info("[" + str(i) + f"]  {a['ftype']} : {a['dbname']}  ({verified})\n\n {a['answer']} ")
                #st.info("[" + str(i) + f"]  {a['ftype']} : {a['dbname']}  (verified= {str(a['verified'])})\n\n {a['answer']} ")

            st.info("[end of response]")

if __name__ == "__main__":
    main()
