from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from rag_mvp.config import Settings
from rag_mvp.embeddings import build_embeddings


SYSTEM_PROMPT = """You are a helpful assistant for question answering.
Use only the provided context to answer.
If the answer is not present in the context, say:
"I don't know based on the provided documents."
"""


def retrieve_context(settings: Settings, question: str) -> list[Document]:
    embeddings = build_embeddings(settings)
    db = Chroma(
        persist_directory=str(settings.db_dir),
        embedding_function=embeddings,
    )
    retriever = db.as_retriever(search_kwargs={"k": settings.top_k})
    return retriever.invoke(question)


def answer_question(settings: Settings, question: str) -> tuple[str, list[Document]]:
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Set it in your .env file.")
    if not settings.db_dir.exists():
        raise ValueError(
            f"Vector database not found at {settings.db_dir}. Run ingest first."
        )

    docs = retrieve_context(settings, question)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
        ]
    )
    llm = ChatGoogleGenerativeAI(model=settings.gemini_model, temperature=0)
    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})
    return response.content, docs
