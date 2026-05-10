"""Document ingestion pipline."""

import requests
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.document import Document

def download_pdf(url: str) -> Path:
    """
    Download a PDF from the given URL and save it to a local path.

    :param url: The URL of the PDF to download.
    :return: Path to the downloaded PDF file.
    """
    # It might not be optimal to download the PDF to disk, but it is a simple solution for now.
    # Might need some type of value error hangling - come back later.
    pass

def load_pdf(path: Path) -> list:
    """
    Load a PDF file from disk and parse it into LangChain documents

    :param path: Path to the PDF file on the disk.
    :return: List of langchain objects representing the PDF content.
    """
    pass

def chunck_docuument(docs: list) -> list:
    """
    Chunk the documents into smaller pieces to be ingested into the vector store.

    :param docs: List of all the langchain documents to be split.
    :return: List of all the langchain documents after being split into smaller pieces.
    """
    pass

def build_vector_store(chunks: list) -> FAISS:
    """
    Build a FAISS vector store from the given document chunks.

    Use OPENAI embeddings to create the vector store.
    This will allow us to perform semantic search on the documents later on.

    :param chunks: List of all the langchain documents to be ingested into the vector store.
    :return: FAISS vecror store containing the document chunks and their corresponding embeddings.
    """
    pass

def ingest(url: str) -> FAISS:
    """
    Run the full ingestion pipline for a ssingle PDF URL.

    :param url:
    :return:
    """
    pass
