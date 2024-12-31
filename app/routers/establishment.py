# updated establishment.py
 
import base64
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from app.prompts.prompt import (
    RESEARCH_AGENT_PROMPT,
    HYPOTHESIS_GENERATION_PROMPT,
    NON_COMPLIANCE_WORDS,
)
from app.services.doc_gen import doc_gen
from llama_index.core.tools import FunctionTool
from llama_index.readers.semanticscholar import SemanticScholarReader
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage
 
router = APIRouter()
 
missing_json = "Bad Request: Required JSON fields are missing."
 
 
@router.post("/hypothesis_wrt_rootcause")
async def hypothesis_gen(request: Request):
    llm = request.app.state.llm
 
    try:
        data = await request.json()
 
        # Extract fields from JSON
        event_description = data["event_description"]
        product_name = data["product_name"]
        test_name = data["test_name"]
        instrument_name = data["instrument_name"]
        detail_visual_symptoms = data["detail_visual_symptoms"]
        immediate_actions = data["immediate_actions"]
        incident_type = data["incident_type"]
        root_cause = data["root_cause"]
 
    except KeyError:
        raise HTTPException(status_code=400, detail=missing_json)
 
    incident = f"Name: {product_name}, Instrument Name: {instrument_name}, Test Name: {test_name}, event Description: {event_description}, Detailed visual symptoms: {detail_visual_symptoms}, Immediate Actions: {immediate_actions}, Incident Type: {incident_type} Root cause: {root_cause}"
 
    query = (
        HYPOTHESIS_GENERATION_PROMPT.format(incident=incident) + NON_COMPLIANCE_WORDS
    )
 
    response = await llm.acomplete(query)
 
    doc = doc_gen(str(response))
 
    # Convert the BytesIO to Base64
    base64_encoded = base64.b64encode(doc.read()).decode("utf-8")
 
    # Return Base64 string
    return {"filename": "hypothesis.docx", "file": base64_encoded}
 
 
# Raise error function
def raise_error():
    """Used to raise error if no article is found."""
    raise ValueError("No relevant research articles found for this specific incident.")
 
 
@router.post("/research_material")
async def research_material(request: Request):
    """
    Route to fetch research material using Semantic Scholar and a ReAct agent.
    """
 
    llm = request.app.state.llm
    sllm_research = request.app.state.sllm_3
 
    s2reader = SemanticScholarReader()
    required_fields = ["product_name", "test_name", "instrument_name", "root_cause"]
 
    # Parse request data
    try:
        data = await request.json()
        # Check for missing fields
        missing_fields = [
            field
            for field in required_fields
            if field not in data or not str(data[field]).strip()
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}",
            )
 
        # Extract fields from JSON
        product_name = data["product_name"]
        test_name = data["test_name"]
        instrument_name = data["instrument_name"]
        root_cause = data["root_cause"]
 
    except KeyError:
        raise HTTPException(status_code=400, detail=missing_json)
 
    # Define tools
    scholar_search_tool = FunctionTool.from_defaults(fn=s2reader.load_data)
    raise_value_error = FunctionTool.from_defaults(fn=raise_error)
 
    # Initialize ReAct agent
    agent = ReActAgent.from_tools(
        [scholar_search_tool, raise_value_error],
        llm=llm,
        verbose=True,
        max_iterations=10,
    )
 
    query = RESEARCH_AGENT_PROMPT.format(
        input=f"Product Name: {product_name}, Instrument Name: {instrument_name}, Test Name: {test_name}, Root Cause: {root_cause}"
    )
 
    # Run the agent with error handling
    try:
        response = agent.chat(query)
        response = str(response)
        input_msg = ChatMessage.from_str(response)
        response = await sllm_research.achat([input_msg])
    except ValueError:
        return {
            "message": "The system was not able to find any relevant research articles for this specific incident."
        }
 
    # Return the response
    return response.raw.json()
 
 
@router.post("/establishment_summary")
async def establishment_summary_gen(request: Request):
    """
    Generate an establishment summary of the root cause based on the provided inputs.
    """
 
    llm = request.app.state.llm
 
    try:
        data = await request.json()
    except KeyError:
        raise HTTPException(status_code=400, detail=missing_json)
 
    incident = str(data)
 
    query = (
        "Provide a brief establishment summary of the root cause based on the inputs provided. "
        + incident
        + NON_COMPLIANCE_WORDS
    )
 
    response = await llm.acomplete(query)
 
    return str(response)