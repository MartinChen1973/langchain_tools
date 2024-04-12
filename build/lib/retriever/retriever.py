# for md
from math import e
from pdb import run
from retriever.md.split_md import parse_markdown
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch

# for search
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

class LangChainRetriever:
    """
    A retriever class for creating search indexes from markdown files or web content.

    This class provides functionality to create retrievers that can search through
    content indexed from markdown files or fetched from URLs. It also supports creating
    runnable objects from markdown files which can be used to execute search queries
    in parallel with additional processing.

    Methods:
        create_retriever_from_file(file_path, embedding): Create a retriever from a markdown file.
        createRetrieverFromUrl(url): Create a retriever from a URL.
        create_runnable_from_file(file_path, embedding): Create a runnable from a markdown file.
    """

    @staticmethod
    def create_runnable_from_file(file_path, embedding=None):
        """
        Create a Runnable object from a markdown file which facilitates parallel execution 
        of search queries against the indexed text along with additional processing.

        This method creates a retriever from the markdown file and wraps it into a RunnableParallel
        object. This allows for executing search queries in parallel, combining the search context
        with additional passthrough operations.

        Parameters:
            file_path (str): Path to the markdown file.
            embedding (OpenAIEmbeddings, optional): Embedding model to use for text vectorization.

        Returns:
            A RunnableParallel object configured with the retriever and a passthrough for questions.
        """
        retriever = LangChainRetriever.create_retriever_from_file(file_path, embedding)
        questionAndContext = RunnableParallel(
            {"context": retriever,
             "question": RunnablePassthrough()}
        )
        return questionAndContext

    @staticmethod
    def create_retriever_from_file(file_path, embedding=None):
        """
        Create a retriever from a markdown file.

        Parameters:
            file_path (str): Path to the markdown file.
            embedding (OpenAIEmbeddings, optional): Embedding model to use for text vectorization.

        Returns:
            A retriever object capable of searching the indexed text.
        
        Raises:
            Exception: If the file type is not supported.
        """
        if embedding is None:
            embedding = OpenAIEmbeddings()

        if file_path.endswith('.md'):
            sections_leave_policy = parse_markdown(file_path)
            vectorstore = DocArrayInMemorySearch.from_texts(sections_leave_policy, embedding=embedding)
            retriever = vectorstore.as_retriever()
            return retriever
        else:
            raise Exception("Unknown file type")

    @staticmethod
    def createRetrieverFromUrl(url: str):
        """
        Create a retriever from web content at the specified URL.

        Parameters:
            url (str): The URL from which to load the content.

        Returns:
            A retriever object capable of searching the indexed web content.
        """
        loader = WebBaseLoader(url)
        docs = loader.load()
        embeddings = OpenAIEmbeddings()
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(docs)
        vector = FAISS.from_documents(documents, embeddings)
        retriever = vector.as_retriever()
        return retriever
