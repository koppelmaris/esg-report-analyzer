"""Multi-document ingestion entry point."""

from langchain_community.vectorstores import FAISS
from app.pipeline import ingest


def ingest_multiple(urls: list[str]) -> FAISS:
    """
    Ingest multiple PDF URLs into a single merged FAISS vector store.

    :param urls: List of PDF URLs to download and index.
    :return: A single FAISS vector store containing chunks from all documents.
    """
    stores = [ingest(url) for url in urls]
    base = stores[0]
    for store in stores[1:]:
        base.merge_from(store)
    return base