"""Document ingestion pipeline."""

import os
import requests
import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def download_pdf(url: str) -> Path:
    """
    Download a PDF from the given URL and save it to a local path.

    :param url: The URL of the PDF to download.
    :return: Path to the downloaded PDF file.
    """
    # Downloading to disk because PyPDFLoader requires a file path, not a stream.
    response = requests.get(url)
    response.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(response.content)
    tmp.close()
    return Path(tmp.name)


def load_pdf(path: Path) -> list:
    """
    Load a PDF file from disk and parse it into LangChain documents.

    :param path: Path to the PDF file on disk.
    :return: List of LangChain documents representing the PDF content.
    """
    loader = PyPDFLoader(str(path))
    return loader.load()


def chunk_documents(docs: list) -> list:
    """
    Split documents into smaller chunks for vector store ingestion.

    :param docs: List of LangChain documents to split.
    :return: List of LangChain documents split into smaller pieces.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)


def build_vector_store(chunks: list) -> FAISS:
    """
    Build a FAISS vector store from the given document chunks.

    Uses OpenAI embeddings to enable semantic search over the documents.

    :param chunks: List of LangChain document chunks to index.
    :return: FAISS vector store containing the chunks and their embeddings.
    """
    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(chunks, embeddings)


def ingest(url: str) -> FAISS:
    """
    Run the full ingestion pipeline for a single PDF URL.

    Downloads the PDF, parses it, chunks it, and indexes it into a vector store.

    :param url: The URL of the PDF to ingest.
    :return: FAISS vector store ready for retrieval.
    """
    path = download_pdf(url)
    try:
        docs = load_pdf(path)
        chunks = chunk_documents(docs)
        return build_vector_store(chunks)
    finally:
        os.unlink(path)