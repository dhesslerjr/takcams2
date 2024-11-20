"""
PythiaAI-Lab Code Structure:

1. Imports: Required libraries for the application.
2. Environment Setup: Checking for GROQ API key.
3. TextDatabase Class:
   - Manages text-based databases (PRIMARY_SOP and ADDENDUM_SOP).
   - Methods: __init__, add_document, save, search.
4. PythiaAILab Class:
   - Core functionality of the application.
   - Attributes: primary_sop, addendum_sop, prompts.
   - Methods:
     - create_databases: Process SOP and additional sources.
     - process_sop: Handle SOP file (PDF or text).
     - process_additional_sources: Process web pages and PDFs.
     - ask_question: Main question-answering logic.
     - search_primary_sop: Search PRIMARY_SOP for answers.
     - search_additional_sources: Generate and verify potential answers.
5. Main Function:
   - Streamlit UI setup and main application loop.
   - Handles user inputs, database creation, and question-answering process.
6. Execution: Run the main function when the script is executed.

The code follows a modular structure, separating database management, core logic, and user interface. It implements all required steps, including user inputs, database creation and updating, LLM interactions, and runtime outputs.
"""

import streamlit as st
import os
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import groq
import sys
from dotenv import load_dotenv
import re
from pathlib import Path
import tempfile

print("Current working directory:", os.getcwd())
print(".env file exists:", os.path.exists('.env'))

load_dotenv(verbose=True)

groq_api_key = os.getenv("GROQ_API_KEY")
print("GROQ_API_KEY loaded:", bool(groq_api_key))

if not groq_api_key:
    st.error("GROQ API key not found. Please check your .env file.")
    st.stop()

client = groq.Client(api_key=groq_api_key)

class TextDatabase:
    """
    A class to manage text-based databases for storing and searching information.

    This class provides functionality to create, update, and search within a text file,
    which serves as a simple database for the PythiaAI-Lab application.
    """

    def __init__(self, filename):
        """
        Initialize the TextDatabase with a given filename.

        Args:
            filename (str): The name of the file to use as the database.
        """
        self.filename = filename
        self.content = ""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.content = f.read()

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

class PythiaAILab:
    """
    The main class for the PythiaAI-Lab application.

    This class manages the databases, processes user queries, and interacts with the GROQ API
    to provide answers to laboratory-related questions.
    """

    def __init__(self):
        """
        Initialize the PythiaAILab with databases and predefined prompts.
        """
        self.primary_sop = None
        self.additional_sops = []
        self.additional_databases = {}
        self.prompts = {
            "system": "You are an AI assistant specialized in laboratory procedures and protocols. "
                      "Your role is to provide accurate, concise, and helpful information based on "
                      "the Standard Operating Procedures (SOPs) and additional verified sources. "
                      "Always prioritize safety and accuracy in your responses.",

            "query": "Based on the following context from our Standard Operating Procedures, "
                     "please answer the user's question:\n\nContext: {context}\n\nQuestion: {question}\n\n"
                     "If the context doesn't contain enough information to fully answer the question, "
                     "say so, but provide any relevant information that is available.",

            "generate": "You are tasked with generating an answer to a laboratory-related question "
                        "that isn't directly addressed in our Standard Operating Procedures. "
                        "Use your knowledge of general laboratory practices, safety protocols, and "
                        "scientific principles to provide a helpful response. If you're unsure or if "
                        "the question requires specific institutional knowledge, clearly state that "
                        "the answer should be verified by a supervisor or referring to official documentation.\n\n"
                        "Question: {question}\n\nGenerated Answer:",

            "verify": "You are reviewing a generated answer for accuracy and appropriateness in a "
                      "laboratory context. Evaluate the following answer based on these criteria:\n"
                      "1. Accuracy of scientific information\n"
                      "2. Adherence to general lab safety principles\n"
                      "3. Clarity and conciseness of explanation\n"
                      "4. Appropriate cautions or disclaimers where necessary\n\n"
                      "Answer to evaluate: {answer}\n\n"
                      "Provide a brief assessment and suggest any necessary improvements:"
        }

###FILES - raminderpal###
    def create_databases(self, file_paths, extra_dbs):
        if not file_paths:
            raise ValueError("At least one SOP file is required.")

        st.info("Creating PRIMARY_SOP database...")
        self.primary_sop = self.process_sop(file_paths[0])
        
        if len(file_paths) > 1:
            st.info("Processing additional SOP documents...")
            for path in file_paths[1:]:
                self.additional_sops.append(self.process_sop(path))
        
        for db_name, db_path in extra_dbs.items():
            st.info(f"Creating {db_name} database...")
            self.additional_databases[db_name] = self.process_extra_database(db_name, db_path)
            

    def process_sop(self, file_path):
        # Read the file and create a TextDatabase
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        db = TextDatabase(content)
        st.success(f"Processed SOP: {Path(file_path).name}")
        return db

            
        
    def process_extra_database(self, db_name, db_path):
        # Read the file and create a TextDatabase
        with open(db_path, 'r', encoding='utf-8') as file:
            content = file.read()
        db = TextDatabase(content)
        st.success(f"Created {db_name} database")
        return db

###STREAMED - david###
    def create_databases_fromstream(self, sop_files, extra_dbs):
        if not sop_files:
            raise ValueError("At least one SOP file is required.")

        st.info("Creating PRIMARY_SOP database...")
        self.primary_sop = self.process_sop_stream(sop_files[0])
        
        if len(sop_files) > 1:
            st.info("Processing additional SOP documents...")
            for f in sop_files[1:]:
                self.additional_sops.append(self.process_sop_stream(f))
        
        for db in extra_dbs:
            st.info(f"Creating {db.name} database...")
            self.additional_databases[db.name] = self.process_extra_database_stream(db)

    def process_sop_stream(self,f):
        db = TextDatabase(f.read())
        st.success(f"Processed SOP: {f.name}")
        return db

    def process_extra_database_stream(self, f):
        # Read the file and create a TextDatabase
        db = TextDatabase(f.read())
        st.success(f"Created {f.name} database")
        return db

    def ask_question(self, question):
        """
        Process a user's question by searching the PRIMARY_SOP and, if necessary, additional sources.
        Includes an independent check for relevance and accuracy.

        Args:
            question (str): The user's question.

        Returns:
            bool: True if an answer was found and verified, False otherwise.
        """
        st.info(f"Searching PRIMARY_SOP for answer to: {question}")
        primary_answer = self.search_sop(self.primary_sop, question)
        
        if primary_answer:
            if self.verify_answer(question, primary_answer):
                st.success("Answer found in PRIMARY_SOP:")
                st.write(primary_answer)
                st.info("Source: PRIMARY_SOP")
                return True
            else:
                st.warning("Answer found in PRIMARY_SOP but failed verification. Searching additional sources...")
        else:
            st.warning("Answer not found in PRIMARY_SOP. Searching additional sources...")
        
        return self.search_additional_sources(question)

    def verify_answer(self, question, answer):
        """
        Independently verify the relevance and accuracy of the answer.

        Args:
            question (str): The user's original question.
            answer (str): The generated answer to verify.

        Returns:
            bool: True if the answer is relevant and accurate, False otherwise.
        """
        verification_prompt = f"""
        You are an expert in laboratory procedures and protocols. Your task is to verify the relevance and accuracy of an answer to a given question.

        Question: {question}

        Answer: {answer}

        Please evaluate the answer based on the following criteria:
        1. Relevance: Does the answer directly address the question?
        2. Accuracy: Is the information provided in the answer correct and up-to-date?
        3. Completeness: Does the answer provide sufficient information to fully address the question?

        Respond with either 'VERIFIED' if the answer meets all criteria, or 'NOT VERIFIED' if it fails on any point. 
        Do not provide any explanation, just the verification status.
        """

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": verification_prompt}],
            temperature=0.0,
            max_tokens=1000
        )
        
        verification_result = response.choices[0].message.content.strip().upper()
        return verification_result == "VERIFIED"

    def search_sop(self, sop_db, question):
        context = sop_db.search(question)[0] if sop_db.search(question) else ""
        if context:
            prompt = self.prompts["system"] + "\n" + self.prompts["query"].format(context=context, question=question)
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        return None

    def search_additional_sources(self, question):
        for i, sop in enumerate(self.additional_sops):
            answer = self.search_sop(sop, question)
            if answer and self.verify_answer(question, answer):
                st.info(f"Verified answer found in additional SOP document {i+1}:")
                st.write(answer)
                st.info(f"Source: Additional SOP document {i+1}")
                return True

        for db_name, db in self.additional_databases.items():
            answer = self.search_sop(db, question)
            if answer and self.verify_answer(question, answer):
                st.info(f"Verified answer found in {db_name}:")
                st.write(answer)
                st.info(f"Source: {db_name}")
                return True

        st.warning("No verified answer found in any source. Generating new answer...")
        return self.generate_and_verify_answer(question)

    def generate_and_verify_answer(self, question):
        prompt = self.prompts["system"] + "\n" + self.prompts["generate"].format(question=question)
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=1000
        )
        potential_answer = response.choices[0].message.content.strip()
        
        if self.verify_answer(question, potential_answer):
            st.info("Verified answer generated:")
            st.write(potential_answer)
            st.info("Source: Generated Answer (added to ADDENDUM_SOP)")
            self.additional_sops.append(TextDatabase(potential_answer))
            st.success("Answer added to additional SOPs.")
            return True
        else:
            st.warning("Generated answer failed verification. Unable to provide a verified answer.")
            return False

def main():
    """
    The main function that sets up the Streamlit UI and manages the application flow.
    """
    st.title("PythiaAI-Lab")
    
    if 'pythia' not in st.session_state:
        st.session_state.pythia = PythiaAILab()
        st.session_state.databases_created = False

    if not st.session_state.databases_created:
        st.header("Database Creation")

        # Multiple file uploader
        uploaded_files = st.file_uploader("Upload SOP document(s)", type=['txt', 'pdf'], accept_multiple_files=True)

        if uploaded_files:
            st.write("Uploaded SOP files:")
            for file in uploaded_files:
                st.write(f"- {file.name}")

        #extra_databases = st.text_area("Enter additional documents by file path (one per line)", help="Optional")
       # extra_databases file uploader
        extra_databases = st.file_uploader("Upload extra database document(s)", type=['txt', 'pdf'], accept_multiple_files=True)



        if st.button("Create Databases"):
 
            if uploaded_files:
                if False:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        file_paths = []
                        for file in uploaded_files:
                            file_path = Path(temp_dir) / file.name
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            file_paths.append(str(file_path))

                        extra_dbs = []        
                        for line in extra_databases.split('\n'):
                                if ':' in line:
                                    name, path = line.split(':')
                                    extra_dbs[name.strip()] = path.strip()
                        
                    st.session_state.pythia.create_databases(file_paths, extra_dbs)
                else:
                    st.session_state.pythia.create_databases_fromstream(uploaded_files, extra_databases)
                    
                
                st.session_state.databases_created = True
                st.success("Databases created successfully!")
            else:
                st.error("Please upload at least one SOP file.")

    if st.session_state.databases_created:
        st.header("Ask Questions")
        question = st.text_input("Enter your question (or type 'END' to exit)")
        
        if question.lower() == 'end':
            st.info("Thank you for using PythiaAI-Lab. Goodbye!")
            st.stop()
        
        if question:
            st.session_state.pythia.ask_question(question)

if __name__ == "__main__":
    main()
