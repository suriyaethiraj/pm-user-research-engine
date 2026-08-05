from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class PainPoint(BaseModel):
    title: str
    description: str
    frequency: str        # "Mentioned once" / "Recurring" / "Dominant theme"
    severity: str         # High / Medium / Low
    confidence: str       # High / Medium / Low
    direct_quote: str


class Motivation(BaseModel):
    title: str
    description: str
    underlying_driver: str
    confidence: str


class UnmetNeed(BaseModel):
    title: str
    description: str
    current_workaround: str
    opportunity_size: str   # High / Medium / Low
    confidence: str


class JTBDStatement(BaseModel):
    situation: str
    motivation: str
    outcome: str
    full_statement: str   # "When I [situation], I want to [motivation], so I can [outcome]"


class PersonaSignal(BaseModel):
    dimension: str        # e.g. "Tech savviness", "Role seniority"
    observed_value: str
    evidence: str


class SentimentEntry(BaseModel):
    topic: str
    sentiment: str        # Positive / Negative / Neutral / Mixed
    intensity: str        # Strong / Moderate / Mild
    representative_quote: str


class NotableQuote(BaseModel):
    quote: str
    context: str
    insight_category: str  # pain_point / motivation / unmet_need / jtbd / general
    significance: str


class FollowUpQuestion(BaseModel):
    question: str
    rationale: str
    priority: str         # Must ask / Nice to have


class PMAction(BaseModel):
    action: str
    category: str         # Roadmap / Research / Design / Stakeholder
    priority: str         # P0 / P1 / P2
    rationale: str


class InterviewInsights(BaseModel):
    interview_id: str
    participant_label: str    # e.g. "P1 — Senior PM at Series B startup"
    interview_date: str
    duration_minutes: Optional[int] = None
    transcript_source: str    # audio / text / document
    executive_summary: str
    pain_points: List[PainPoint]
    motivations: List[Motivation]
    unmet_needs: List[UnmetNeed]
    jtbd_statements: List[JTBDStatement]
    persona_signals: List[PersonaSignal]
    sentiment_map: List[SentimentEntry]
    notable_quotes: List[NotableQuote]
    follow_up_questions: List[FollowUpQuestion]
    pm_actions: List[PMAction]
    overall_sentiment: str    # Positive / Negative / Neutral / Mixed
    research_confidence: str  # High / Medium / Low
    tags: List[str]


class CrossInterviewPattern(BaseModel):
    pattern_title: str
    pattern_type: str         # pain_point / motivation / unmet_need / jtbd / sentiment
    description: str
    frequency: int            # how many interviews mention this
    interview_ids: List[str]
    supporting_quotes: List[str]
    confidence: str
    pm_implication: str


class CrossInterviewReport(BaseModel):
    total_interviews: int
    interviews_analyzed: List[str]
    generated_at: str
    top_themes: List[str]
    patterns: List[CrossInterviewPattern]
    consensus_pain_points: List[str]
    divergent_findings: List[str]
    recommended_next_research: List[str]
    synthesis_narrative: str
