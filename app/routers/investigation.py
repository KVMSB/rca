import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from llama_index.core.llms import ChatMessage
from app.prompts.prompt import (
    PHASE_I_INVESTIGATION_QA_PROMPT,
    PHASE_II_INVESTIGATION_QA_PROMPT,
    NON_COMPLIANCE_WORDS,
)
from typing import Any

from app.prompts.prompt import DOMINANT_ROOT_CAUSE_PROMPT, RCA_CAPA_PROMPT

# Router instance for this module
router = APIRouter()


# Dependency to inject application state
def get_services(request: Request) -> Any:
    """Dependency to fetch application state."""
    return request.app.state


@router.post("/investigation_questions")
async def investigation_questions(
    data: dict,  # Expect JSON payload from the client
    services=Depends(get_services),
):
    """
    Endpoint to handle investigation questions.
    """

    sllm_questions = services.sllm_1

    # Extract and validate fields from JSON
    required_fields = [
        "event_description",
        "description_of_incident",
        "product_name",
        "test_name",
        "instrument_name",
        "detail_visual_symptoms",
        "immediate_actions",
        "incident_type",
    ]
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=400, detail=f"Bad Request: '{field}' is missing."
            )

    # Build the incident string
    incident = (
        f"Name: {data['product_name']}, Instrument Name: {data['instrument_name']}, "
        f"Test Name: {data['test_name']}, Event Description: {data['event_description']}, "
        f"Description of Incident: {data['description_of_incident']}, "
        f"Detailed Visual Symptoms: {data['detail_visual_symptoms']}, "
        f"Immediate Actions: {data['immediate_actions']}"
    )

    # Choose prompt based on incident type
    if data["incident_type"] == "Phase-I":
        query = PHASE_I_INVESTIGATION_QA_PROMPT.format(input=incident)
    else:
        query = PHASE_II_INVESTIGATION_QA_PROMPT.format(incident=incident)
    # Process response and return the output
    input_msg = ChatMessage.from_str(str(query))
    set_of_questions = await sllm_questions.achat([input_msg])
    parsed_json = json.loads(set_of_questions.raw.json())

    # Return the parsed JSON as a response
    return JSONResponse(content=parsed_json)


@router.post("/probable_root_causes")
async def root_cause_capa(payload: dict, services=Depends(get_services)):
    try:
        # Extract services from dependencies
        sllm_rca = services.sllm_2
        rag = services.rag

        # Extract JSON fields
        investigations = payload
        event_description = investigations["incident"]["event_description"]
        product_name = investigations["incident"]["product_name"]
        test_name = investigations["incident"]["test_name"]
        instrument_name = investigations["incident"]["instrument_name"]
        detail_visual_symptoms = investigations["incident"]["detail_visual_symptoms"]
        immediate_actions = investigations["incident"]["immediate_actions"]
        questions = investigations["questions"]

    except KeyError as ke:
        raise HTTPException(status_code=400, detail=f"Missing key: {str(ke)}")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid value: {str(ve)}")

    # Generate the query for the dominant root cause
    query_dominant_root_cause = DOMINANT_ROOT_CAUSE_PROMPT.format(
        event=f"Name: {product_name}, Instrument Name: {instrument_name}, Test Name: {test_name}, "
        f"event Description: {event_description}, "
        f"Detailed visual symptoms: {detail_visual_symptoms}, Immediate Actions: {immediate_actions}, investigation questions answered by practitioner : {questions}"
    )
    historically_dominant_root_cause = rag.search(query_dominant_root_cause)

    # Format prompt for RCA CAPA
    prompt = (
        RCA_CAPA_PROMPT.format(
            investigations=investigations,
            historical_context=historically_dominant_root_cause,
        )
        + NON_COMPLIANCE_WORDS
    )
    input_msg = ChatMessage.from_str(prompt)

    # Get structured output for probable root causes and CAPA
    probable_dominant_rootcause_capa = await sllm_rca.achat([input_msg])

    parsed_json = json.loads(probable_dominant_rootcause_capa.raw.json())
    return JSONResponse(content=parsed_json)
