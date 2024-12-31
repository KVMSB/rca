from fastapi import Depends, Request


def get_sllm_questions(request: Request):
    """
    Dependency to retrieve the structured LLM for questions from app state
    """
    return request.app.state.sllm_1


def get_rag_service(request: Request):
    """
    Dependency to retrieve the RAG service from app state
    """
    return request.app.state.rag
