"""Document ingestion pipeline."""

import tempfile
from pathlib import Path

import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DOWNLOAD_TIMEOUT = 60


def download_pdf(url: str) -> Path:
    """
    Download a PDF from the given URL and save it to a temporary local file.

    :param url: The URL of the PDF to download.
    :return: Path to the downloaded PDF file on disk.
    :raises requests.HTTPError: If the download request fails.
    """
    response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    response.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(response.content)
    tmp.close()
    return Path(tmp.name)


def load_pdf(path: Path) -> list[Document]:
    """
    Load a PDF file from disk and parse it into LangChain documents.

    Each page of the PDF becomes a separate Document object with
    page number stored in metadata.

    :param path: Path to the PDF file on disk.
    :return: List of LangChain Document objects, one per page.
    """
    loader = PyPDFLoader(str(path))
    return loader.load()


def chunk_document(docs: list[Document]) -> list[Document]:
    """
    Split documents into smaller overlapping chunks for retrieval.

    Uses RecursiveCharacterTextSplitter which tries to split on natural
    boundaries (paragraphs, sentences) before falling back to characters,
    preserving context better than a fixed-size split.

    :param docs: List of LangChain Document objects to split.
    :return: List of smaller Document chunks with preserved metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(docs)


def build_vector_store(chunks: list[Document]) -> FAISS:
    """
    Build a FAISS vector store from the given document chunks.

    Uses a local HuggingFace embedding model (all-MiniLM-L6-v2) — no API
    key required. Converts chunks into vectors for semantic similarity search.

    :param chunks: List of LangChain Document chunks to embed and index.
    :return: FAISS vector store containing all chunks and their embeddings.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.from_documents(chunks, embeddings)


def ingest(url: str) -> FAISS:
    """
    Run the full ingestion pipeline for a single PDF URL.

    Downloads the PDF, parses it, chunks it, and returns a searchable
    FAISS vector store.

    :param url: URL of the PDF to ingest.
    :return: FAISS vector store ready for similarity search.
    """
    path = download_pdf(url)
    docs = load_pdf(path)
    chunks = chunk_document(docs)
    return build_vector_store(chunks)


def ingest_multiple(urls: list[str]) -> FAISS:
    """
    Ingest multiple PDFs and merge them into a single vector store.

    Useful when a company's report is split across multiple documents.
    All chunks are merged into one FAISS index so retrieval searches
    across all documents simultaneously.

    :param urls: List of PDF URLs to ingest and merge.
    :return: Single FAISS vector store containing all documents.
    """
    stores = [ingest(url) for url in urls]
    base = stores[0]
    for store in stores[1:]:
        base.merge_from(store)
    return base
