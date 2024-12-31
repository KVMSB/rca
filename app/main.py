import logging
from fastapi import FastAPI
from app.services.llm_services import LLMService
from app.services.rag_service import RAGService
from llama_index.core import SimpleDirectoryReader
from app.routers import (
    establishment,
    investigation,
    impact_and_final_summary,
    training_material_gen,
)

from app.services.structured_output import (
    event_investigation_questions_format,
    probable_root_causes_format,
    research_outputs,
    impact_assessment_format,
    hypothesis_report,
)
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="Event Investigation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(investigation.router)
app.include_router(establishment.router)
app.include_router(impact_and_final_summary.router)
app.include_router(training_material_gen.router)

# Initialize services and models
llm_initializer = LLMService("../config.json")
llm, embed_model = llm_initializer.get_llm(), llm_initializer.get_embed_model()

logging.info("LLM initialized")

# Structured LLMs
sllm = llm.as_structured_llm(output_cls=event_investigation_questions_format)
sllm_rca = llm.as_structured_llm(output_cls=probable_root_causes_format)
sllm_research = llm.as_structured_llm(output_cls=research_outputs)
sllm_hypothesis = llm.as_structured_llm(output_cls=hypothesis_report)
sllm_impact_assessment = llm.as_structured_llm(output_cls=impact_assessment_format)

logging.info("Structured output LLMs initialized")

# Load documents
documents = SimpleDirectoryReader("../data/").load_data()
rag = RAGService(documents)

logging.info("RAG is up and running")

# Store global services and models
app.state.llm = llm
app.state.sllm_1 = sllm
app.state.sllm_2 = sllm_rca
app.state.sllm_3 = sllm_research
app.state.sllm_4 = sllm_hypothesis
app.state.sllm_5 = sllm_impact_assessment
app.state.rag = rag
