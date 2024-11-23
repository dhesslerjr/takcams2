import os, random, json
import groq
import sys
import re
import tempfile
import streamlit as st




class TakCamsAI:
    def __init__(self, groq_key):
        
        self.groq_api_key = groq_key
        self.client = groq.Client(api_key=groq_key)
        self.contexts = []

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

    def set_contexts(self,contexts_array):            
        self.contexts=[]
        for c in contexts_array:
             self.contexts.append(c)

    
    def get_hint(self):
        return f"random hint " + str(random.random())

    def query_database(self,database,aquestion):

        answer=""
        if database.content:
                prompt = self.prompts["system"] + "\n" + self.prompts["query"].format(context=database.content, question=aquestion)

                response = self.client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=1000
                )
                answer=response.choices[0].message.content.strip()
        return answer


    def ask_question(self, question):
            """
            Process a user's question by searching the PRIMARY_SOP and, if necessary, additional sources.
            Includes an independent check for relevance and accuracy.

            Args:
                question (str): The user's question.

            Returns:
                bool: True if an answer was found and verified, False otherwise.
            """
            responses=[]
            if len(self.contexts)>0:
                for c in self.contexts:

                    an_answer=self.query_database(c,question)
                    if(an_answer):   
                        isverified=self.verify_answer(question,an_answer)
                        obj={'ftype':c.ftype, 'dbname':c.name, 'answer':an_answer, 'verified':isverified}
                        responses.append(obj)
            
            return responses

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

            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": verification_prompt}],
                temperature=0.0,
                max_tokens=1000
            )
            
            verification_result = response.choices[0].message.content.strip().upper()
            return verification_result == "VERIFIED"
