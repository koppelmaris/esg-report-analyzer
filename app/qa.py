"""Retrieval and answer generation."""

from anthropic import Anthropic
from langchain_community.vectorstores import FAISS
from app.models import Answer, CompanyReport, SourceCitation
import json

client = Anthropic()

QUESTIONS = [
    "What are the company's main ESG goals?",
    "What emissions targets has the company set?",
    "How does the company approach employee wellbeing?",
    "What governance structures are in place for sustainability?",
    "What progress has been made on environmental initiatives?",
]

SUMMARY_PROMPT = """You are an ESG analyst. Based on the following excerpts from a company report,
write a concise 3-5 sentence summary of the company's overall ESG position.

Excerpts:
{context}

Summary:"""

QA_PROMPT = """You are an ESG analyst. Answer the question using ONLY the provided excerpts.
If the answer is not present in the excerpts, respond with exactly: NOT_FOUND

Question: {question}

Excerpts (each has a page number):
{context}

Respond in JSON format:
{{
  "answer": "your answer here or null if not found",
  "status": "found" or "not_found",
  "confidence": "high", "medium", or "low",
  "page": <page number where answer was found, or null>,
  "quote": "short verbatim phrase from the excerpt, or null"
}}

Rules:
- confidence "high" = answer is stated directly
- confidence "medium" = answer is implied or partially stated
- confidence "low" = answer is loosely inferred
- If not found, set status=not_found, everything else null
"""


def format_chunks(chunks: list) -> str:
    """
    Format a list of retrieved document chunks into a single prompt-ready string.

    Each chunk is prefixed with its page number so the LLM can reference
    the source when generating an answer.

    :param chunks: List of LangChain Document objects returned by the vector store.
    :return: A single string with each chunk separated by a blank line,
             formatted as '[Page N]: <content>'.
    """
    parts = []
    for doc in chunks:
        page = doc.metadata.get("page", "?")
        parts.append(f"[Page {page}]: {doc.page_content.strip()}")
    return "\n\n".join(parts)


def retrieve(vectorstore: FAISS, query: str, k: int = 5) -> list:
    """
    Retrieve the top-k most semantically relevant chunks for a given query.

    Uses FAISS cosine similarity search over OpenAI embeddings to find
    the chunks most likely to contain the answer.

    :param vectorstore: FAISS vector store built from the ingested PDF.
    :param query: The search query or question to retrieve chunks for.
    :param k: Number of chunks to retrieve. Defaults to 5.
    :return: List of LangChain Document objects ranked by relevance.
    """
    return vectorstore.similarity_search(query, k=k)


def generate_summary(vectorstore: FAISS) -> str:
    """
    Generate a concise ESG summary for a company based on its report.

    Retrieves a broad set of chunks covering ESG strategy and goals,
    then prompts Claude to synthesise them into a 3-5 sentence overview.

    :param vectorstore: FAISS vector store built from the ingested PDF.
    :return: A plain-text summary of the company's overall ESG position.
    """
    chunks = retrieve(vectorstore, "ESG sustainability overview goals strategy", k=8)
    context = format_chunks(chunks)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": SUMMARY_PROMPT.format(context=context)
        }]
    )
    return response.content[0].text.strip()


def answer_question(vectorstore: FAISS, question: str) -> Answer:
    """
    Retrieve relevant chunks and generate a grounded answer to a single question.

    Performs similarity search to find the most relevant passages, then prompts
    Claude to answer using only those passages. The response is parsed into a
    structured Answer object with confidence level and source citation.
    Returns a not_found Answer if the document lacks the relevant information
    or if the LLM response cannot be parsed.

    :param vectorstore: FAISS vector store built from the ingested PDF.
    :param question: The ESG question to answer.
    :return: An Answer object with status, answer text, confidence level,
             and source citation (page number and quote) if found.
    """
    chunks = retrieve(vectorstore, question, k=5)
    context = format_chunks(chunks)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": QA_PROMPT.format(question=question, context=context)
        }]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        if data.get("status") == "not_found":
            return Answer(status="not_found")
        return Answer(
            status="found",
            answer=data.get("answer"),
            confidence=data.get("confidence"),
            source=SourceCitation(
                page=data.get("page", 0),
                quote=data.get("quote", "")
            )
        )
    except (json.JSONDecodeError, Exception):
        return Answer(status="not_found")


def analyze_company(company_name: str, vectorstore: FAISS) -> CompanyReport:
    """
    Run the full ESG analysis pipeline for a single company.

    Generates an overall summary and answers all predefined questions
    by running retrieval and generation for each one sequentially.

    :param company_name: Display name of the company (used in the report output).
    :param vectorstore: FAISS vector store built from the company's ingested PDF.
    :return: A CompanyReport containing the summary and all question answers.
    """
    summary = generate_summary(vectorstore)
    answers = {}
    for q in QUESTIONS:
        answers[q] = answer_question(vectorstore, q)
    return CompanyReport(company=company_name, summary=summary, questions=answers)
