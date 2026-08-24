"""
AI Job Hunter - LangGraph Orchestrator

Central orchestrator that manages the flow between all agent nodes
using a LangGraph StateGraph with conditional routing.

Architecture: Supervisor pattern where the orchestrator decides which
agent to invoke based on the user's intent/request.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, StateGraph

from backend.agents.nodes.ats_scorer import ats_scorer_node
from backend.agents.nodes.company_research import company_research_node
from backend.agents.nodes.cover_letter import cover_letter_node
from backend.agents.nodes.interview_prep import interview_prep_node
from backend.agents.nodes.job_discovery import job_discovery_node
from backend.agents.nodes.mock_interview import mock_interview_node
from backend.agents.nodes.recruiter_message import recruiter_message_node
from backend.agents.nodes.resume_parser import resume_parser_node
from backend.agents.nodes.resume_tailor import resume_tailor_node
from backend.agents.nodes.salary_negotiation import salary_negotiation_node
from backend.agents.nodes.profile_agent import profile_agent_node
from backend.agents.nodes.job_matching import job_matching_node
from backend.agents.nodes.application_agent import application_agent_node
from backend.agents.nodes.outreach_agent import outreach_agent_node
from backend.agents.nodes.skill_gap_agent import skill_gap_agent_node
from backend.agents.state import AgentState
from backend.utils.logger import get_logger

logger = get_logger("agents.orchestrator")


# Valid agent intents that the orchestrator can route to
AgentIntent = Literal[
    "parse_resume",
    "analyze_ats",
    "tailor_resume",
    "discover_jobs",
    "research_company",
    "generate_cover_letter",
    "generate_recruiter_message",
    "prepare_interview",
    "full_pipeline",
]


def route_by_intent(state: AgentState) -> str:
    """Route to the appropriate agent based on the intent field.

    This is the conditional edge function used by the orchestrator graph
    to decide which node to execute next.

    Args:
        state: The current agent state.

    Returns:
        The name of the next node to execute.
    """
    intent = state.get("intent", "")
    error = state.get("error")

    # If there's an error, go to end
    if error:
        logger.warning("Routing to END due to error", error=error)
        return "end"

    intent_to_node = {
        "parse_resume": "resume_parser",
        "extract_profile": "profile_extractor",
        "analyze_ats": "ats_scorer",
        "match_job": "job_matching_eval",
        "tailor_resume": "resume_tailor",
        "discover_jobs": "job_discovery",
        "research_company": "company_research",
        "generate_cover_letter": "cover_letter_gen",
        "generate_recruiter_message": "recruiter_message_gen",
        "prepare_application": "application_prep",
        "prepare_outreach": "outreach_prep",
        "prepare_interview": "interview_prep_gen",
        "mock_interview": "mock_interview_eval",
        "salary_negotiation": "salary_negotiation_eval",
        "analyze_skill_gap": "skill_gap_eval",
    }

    next_node = intent_to_node.get(intent, "end")
    logger.info("Routing to agent", intent=intent, next_node=next_node)
    return next_node


def route_after_resume_parse(state: AgentState) -> str:
    """Route after resume parsing completes.

    If this is part of a full pipeline, continue to ATS.
    Otherwise, end.
    """
    if state.get("error"):
        return "end"

    intent = state.get("intent", "")
    if intent == "full_pipeline" and state.get("job_description"):
        return "ats_scorer"

    return "end"


def route_after_ats(state: AgentState) -> str:
    """Route after ATS analysis completes.

    For full_pipeline, continue to resume_tailor.
    """
    if state.get("error"):
        return "end"

    intent = state.get("intent", "")
    if intent == "full_pipeline":
        return "resume_tailor"

    return "end"


def build_orchestrator_graph() -> StateGraph:
    """Build and compile the LangGraph orchestrator.

    Creates a StateGraph with nodes for each agent and conditional
    edges for routing between them based on intent.

    Returns:
        Compiled StateGraph ready for invocation.
    """
    logger.info("Building orchestrator graph")

    # Create the graph
    graph = StateGraph(AgentState)

    # --- Add Nodes ---
    graph.add_node("resume_parser", resume_parser_node)
    graph.add_node("profile_extractor", profile_agent_node)
    graph.add_node("ats_scorer", ats_scorer_node)
    graph.add_node("job_matching_eval", job_matching_node)
    graph.add_node("resume_tailor", resume_tailor_node)
    graph.add_node("job_discovery", job_discovery_node)
    graph.add_node("company_research", company_research_node)
    graph.add_node("cover_letter_gen", cover_letter_node)
    graph.add_node("recruiter_message_gen", recruiter_message_node)
    graph.add_node("application_prep", application_agent_node)
    graph.add_node("outreach_prep", outreach_agent_node)
    graph.add_node("interview_prep_gen", interview_prep_node)
    graph.add_node("mock_interview_eval", mock_interview_node)
    graph.add_node("salary_negotiation_eval", salary_negotiation_node)
    graph.add_node("skill_gap_eval", skill_gap_agent_node)

    # --- Set Entry Point ---
    graph.set_conditional_entry_point(
        route_by_intent,
        {
            "resume_parser": "resume_parser",
            "profile_extractor": "profile_extractor",
            "ats_scorer": "ats_scorer",
            "job_matching_eval": "job_matching_eval",
            "resume_tailor": "resume_tailor",
            "job_discovery": "job_discovery",
            "company_research": "company_research",
            "cover_letter_gen": "cover_letter_gen",
            "recruiter_message_gen": "recruiter_message_gen",
            "application_prep": "application_prep",
            "outreach_prep": "outreach_prep",
            "interview_prep_gen": "interview_prep_gen",
            "mock_interview_eval": "mock_interview_eval",
            "salary_negotiation_eval": "salary_negotiation_eval",
            "skill_gap_eval": "skill_gap_eval",
            "end": END,
        },
    )

    # --- Add Conditional Edges ---
    graph.add_conditional_edges(
        "resume_parser",
        route_after_resume_parse,
        {
            "ats_scorer": "ats_scorer",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "ats_scorer",
        route_after_ats,
        {
            "resume_tailor": "resume_tailor",
            "end": END,
        },
    )

    # Terminal nodes
    graph.add_edge("resume_tailor", END)
    graph.add_edge("profile_extractor", END)
    graph.add_edge("job_matching_eval", END)
    graph.add_edge("job_discovery", END)
    graph.add_edge("company_research", END)
    graph.add_edge("cover_letter_gen", END)
    graph.add_edge("recruiter_message_gen", END)
    graph.add_edge("application_prep", END)
    graph.add_edge("outreach_prep", END)
    graph.add_edge("interview_prep_gen", END)
    graph.add_edge("mock_interview_eval", END)
    graph.add_edge("salary_negotiation_eval", END)
    graph.add_edge("skill_gap_eval", END)

    logger.info("Orchestrator graph built successfully")
    return graph


# Compiled graph singleton
_compiled_graph = None


def get_orchestrator():
    """Get the compiled orchestrator graph (singleton).

    Returns:
        Compiled LangGraph ready for invocation.
    """
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_orchestrator_graph()
        _compiled_graph = graph.compile()
        logger.info("Orchestrator graph compiled")
    return _compiled_graph


async def run_agent_pipeline(
    intent: str,
    state_overrides: dict | None = None,
) -> AgentState:
    """Run the agent pipeline with the given intent.

    This is the main entry point for executing agent workflows.

    Args:
        intent: The agent intent (e.g., 'parse_resume', 'analyze_ats').
        state_overrides: Additional state fields to set.

    Returns:
        The final agent state after all nodes have executed.
    """
    orchestrator = get_orchestrator()

    initial_state: AgentState = {
        "intent": intent,
        "current_agent": "orchestrator",
        "error": None,
        **(state_overrides or {}),
    }

    logger.info("Running agent pipeline", intent=intent)

    result = await orchestrator.ainvoke(initial_state)

    if result.get("error"):
        logger.error("Pipeline completed with error", error=result["error"])
    else:
        logger.info("Pipeline completed successfully", intent=intent)

    return result
