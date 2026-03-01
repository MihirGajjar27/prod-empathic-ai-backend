from pydantic import BaseModel


class SessionRecord(BaseModel):
    session_id: str
    created_at_ms: int
    ended_at_ms: int | None = None


class UtteranceRecord(BaseModel):
    utterance_id: str
    session_id: str
    role: str
    text: str
    message_id: str | None = None
    timestamp_ms: int | None = None


class ProsodyFrameRecord(BaseModel):
    frame_id: str
    session_id: str
    message_id: str
    top_scores: dict[str, float]
    created_at_ms: int


class KgNode(BaseModel):
    id: str
    label: str
    canonical: str
    properties: dict


class KgEdge(BaseModel):
    id: str
    type: str
    source: str
    target: str
    properties: dict


class Receipt(BaseModel):
    receipt_id: str
    message_id: str
    tool_name: str
    evidence_quote: str
    applied_node_ids: list[str]
    applied_edge_ids: list[str]
    verified: bool
    warnings: list[str] = []


class KgDiff(BaseModel):
    nodes_upsert: list[KgNode]
    edges_upsert: list[KgEdge]
    receipts: list[Receipt]


class GraphSnapshot(BaseModel):
    nodes: list[KgNode]
    edges: list[KgEdge]


class SessionSummary(BaseModel):
    summary: str
    top_concepts: list[dict]