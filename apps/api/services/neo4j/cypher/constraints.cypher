// Neo4j constraints/indexes

CREATE CONSTRAINT session_id_unique IF NOT EXISTS
FOR (s:Session) REQUIRE s.sessionId IS UNIQUE;

CREATE CONSTRAINT utterance_id_unique IF NOT EXISTS
FOR (u:Utterance) REQUIRE u.utteranceId IS UNIQUE;

CREATE CONSTRAINT prosody_frame_id_unique IF NOT EXISTS
FOR (p:ProsodyFrame) REQUIRE p.frameId IS UNIQUE;

// Add composite uniqueness constraints for all concept labels:
// (sessionId, canonical) on Person, Trigger, Emotion, Belief, Need, Goal, Action, Event.
// I'm having a stroke !!!!!
