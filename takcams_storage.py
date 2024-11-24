import os

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

        #DEBUG
        #st.info(f"created database: {self.name} of type {self.ftype} with content {self.content}")

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
    
    def clear(self):
        self.contexts = []

    def add_context(self,file,ftype):
            newname=os.path.basename(file.filename).replace('"','')
            ftype=ftype
            content=file.read()
            self.contexts.append(TextDatabase(newname,content,ftype))
            #print(f'saving {newname} as {ftype} context: {content}')


