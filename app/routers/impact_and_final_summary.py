from fastapi import APIRouter, Request, HTTPException, Depends
from llama_index.core.llms import ChatMessage
from markdown import markdown
from app.prompts.prompt import (
    FINAL_SUMMARY_PROMPT,
    IMPACT_ASSESSMENT_PROMPT,
    NON_COMPLIANCE_WORDS,
)
 
router = APIRouter()
 
 
# Define the route
@router.post("/impact_assessment")
async def impact_assessment_gen(request: Request):
    """
    Generate an impact assessment based on the provided incident and final root cause.
    """
 
    sllm_impact_assessment = request.app.state.sllm_5
 
    try:
        data = await request.json()
        if "incident" not in data or "final_root_cause" not in data:
            raise KeyError("Missing required keys: 'incident' or 'final_root_cause'")
    except KeyError:
        raise HTTPException(
            status_code=400, detail="Bad Request: Required JSON fields are missing."
        )
 
    incident = str(data)
 
    # Construct the query
    query = IMPACT_ASSESSMENT_PROMPT.format(incident=incident) + NON_COMPLIANCE_WORDS
 
    # Create a chat message
    input_msg = ChatMessage.from_str(str(query))
 
    # Generate the response
    response = await sllm_impact_assessment.achat([input_msg])
 
    return response.raw.json()
 
 
@router.post("/final_summary")
async def final_summary(request: Request):
    """
    Generate a final summary based on the incident, investigation results, and final root cause.
    """
 
    llm = request.app.state.llm
 
    try:
        data = await request.json()
        incident = data["incident"]
        investigation_results = data["impact_assessment"]
        final_root_cause = data["final_root_cause"]
    except KeyError:
        raise HTTPException(
            status_code=400, detail="Bad Request: Required JSON fields are missing."
        )
 
    # Construct the formatted input
    formatted_input = FINAL_SUMMARY_PROMPT.format(
        input=f"issue: {incident} impact assessment: {investigation_results} final root cause: {final_root_cause}"
    )
 
    # Generate the summary
    final_root_cause_summary = await llm.acomplete(formatted_input)
 
    # Convert to HTML using markdown
    html_output = markdown(str(final_root_cause_summary))
 
    return {"html_output": html_output}