from langchain_huggingface import HuggingFaceEmbeddings

from rag_mvp.config import Settings


def build_embeddings(settings: Settings) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)
