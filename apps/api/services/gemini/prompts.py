from typing import Any
import json

from services.gemini.kg_tools import get_allowed_concept_labels, get_allowed_relationship_types


def build_kg_system_prompt() -> str:
    labels = ", ".join(get_allowed_concept_labels())
    relationships = ", ".join(get_allowed_relationship_types())
    return (
        "You're a therapy knowledge graph extraction modle for a live user session and your job\n"
        "is to respond with only the evidence backed tool calls for the current user utterance"
        "Your job is to emit only evidence-backed tool calls for the current user utterance.\n"
        "Graph semantics:\n"
        f"- Allowed concept labels: {labels}.\n"
        f"- Allowed concept-to-concept relationships: {relationships}.\n"
        "- Use `link_utterance_mentions` for transcript-to-concept mention edges.\n"
        "- Use `set_session_goal` only when the user clearly states a goal or desired outcome.\n"
        "- Use `skip_kg_update` when the utterance is ambiguous, purely phatic, too vague, or unsupported by evidence.\n"
        "Evidence rules:\n"
        "- Every mutation tool call must include the current `message_id` and an exact `evidence_quote` substring from the utterance text.\n"
        "- Never quote text that is not present verbatim in the current utterance.\n"
        "- If you are not sure, do not guess; call `skip_kg_update`.\n"
        "Safety and scope rules:\n"
        "- The graph is session-scoped. Do not resolve across sessions.\n"
        "- Prosody scores are expression signals, not emotional truth. Use them only as weak supporting context.\n"
        "- Prefer a small number of precise mutations.\n"
        "- Hard caps per utterance: at most 4 node upserts and at most 6 edge upserts.\n"
        "- Do not use tools to store assistant policy, diagnosis, or unsupported clinical claims."
    )


def build_kg_user_prompt(
    *,
    session_id: str,
    utterance_text: str,
    message_id: str,
    prosody_scores: dict[str, float] | None,
    graph_context: dict[str, Any],
) -> str:
    context_payload = {
        "top_concepts": graph_context.get("top_concepts", []),
        "recent_edges": graph_context.get("recent_edges", []),
        "candidate_matches": graph_context.get("candidate_matches", []),
    }
    return (
        f"session_id: {session_id}\n"
        f"message_id: {message_id}\n"
        f"utterance_text: {utterance_text}\n"
        f"prosody_summary: {summarize_prosody_for_prompt(prosody_scores)}\n"
        f"graph_context_json: {_compact_json(context_payload)}\n"
        "Select the smallest safe set of tool calls for this utterance.\n"
        "If no evidence-backed mutation is justified, call `skip_kg_update`.\n"
        "When linking mentions, include only concepts grounded in the utterance text."
    )


def summarize_prosody_for_prompt(prosody_scores: dict[str, float] | None, top_k: int = 5) -> str:
    if not prosody_scores:
        return "none"
    ranked_scores = sorted(((label, score) for label, score in prosody_scores.items()),key=lambda item: item[1],reverse=True,)[:top_k]
    if not ranked_scores:
        return "none"
    return ", ".join(f"{label}={score:.3f}" for label, score in ranked_scores)


def _compact_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


