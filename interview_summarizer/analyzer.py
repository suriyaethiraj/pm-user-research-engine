from __future__ import annotations
import json
import re
from datetime import datetime
from typing import List
import anthropic
from schema import InterviewInsights, CrossInterviewReport

SYSTEM_PROMPT = """You are a Senior UX Researcher and Product Strategist with 12 years of experience
at Google, IDEO, and top-tier product companies. You extract deep, actionable insights from
user interview transcripts with surgical precision.

RULES:
- Every insight must be grounded in the transcript — never invent or assume
- Direct quotes must be verbatim from the transcript (or closest match)
- Confidence levels reflect how clearly the evidence supports the claim
- JTBD statements follow strict format: "When I [situation], I want to [motivation], so I can [outcome]"
- PM actions must be specific and immediately actionable
- Return ONLY valid JSON — no markdown, no backticks, no explanation"""


def _single_prompt(transcript: str, participant_label: str,
                   interview_id: str, source: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""Analyze this user interview transcript and extract comprehensive structured insights.

INTERVIEW ID: {interview_id}
PARTICIPANT: {participant_label}
DATE: {today}
SOURCE: {source}

TRANSCRIPT:
{transcript[:12000]}

Return a JSON object matching this EXACT schema:
{{
  "interview_id": "{interview_id}",
  "participant_label": "{participant_label}",
  "interview_date": "{today}",
  "duration_minutes": null,
  "transcript_source": "{source}",
  "executive_summary": "3-4 sentence summary of the most important things this participant told us",
  "pain_points": [
    {{
      "title": "Short pain point label",
      "description": "What specifically frustrates them and why",
      "frequency": "Mentioned once | Recurring | Dominant theme",
      "severity": "High | Medium | Low",
      "confidence": "High | Medium | Low",
      "direct_quote": "Verbatim quote from transcript"
    }}
  ],
  "motivations": [
    {{
      "title": "What drives them",
      "description": "Deeper context on this motivation",
      "underlying_driver": "The root psychological or professional driver",
      "confidence": "High | Medium | Low"
    }}
  ],
  "unmet_needs": [
    {{
      "title": "What they need but don't have",
      "description": "Why this need exists and isn't being met",
      "current_workaround": "How they cope today",
      "opportunity_size": "High | Medium | Low",
      "confidence": "High | Medium | Low"
    }}
  ],
  "jtbd_statements": [
    {{
      "situation": "situation context",
      "motivation": "what they want to achieve",
      "outcome": "desired end state",
      "full_statement": "When I [situation], I want to [motivation], so I can [outcome]"
    }}
  ],
  "persona_signals": [
    {{
      "dimension": "e.g. Tech savviness / Decision-making style / Risk tolerance",
      "observed_value": "What we observed",
      "evidence": "Quote or behavior that supports this"
    }}
  ],
  "sentiment_map": [
    {{
      "topic": "Topic area discussed",
      "sentiment": "Positive | Negative | Neutral | Mixed",
      "intensity": "Strong | Moderate | Mild",
      "representative_quote": "Quote showing this sentiment"
    }}
  ],
  "notable_quotes": [
    {{
      "quote": "Verbatim quote",
      "context": "What was being discussed",
      "insight_category": "pain_point | motivation | unmet_need | jtbd | general",
      "significance": "Why this quote matters for product decisions"
    }}
  ],
  "follow_up_questions": [
    {{
      "question": "Specific follow-up question to ask",
      "rationale": "Why this would yield valuable insight",
      "priority": "Must ask | Nice to have"
    }}
  ],
  "pm_actions": [
    {{
      "action": "Specific, immediately actionable task",
      "category": "Roadmap | Research | Design | Stakeholder",
      "priority": "P0 | P1 | P2",
      "rationale": "Why this action is warranted by the transcript"
    }}
  ],
  "overall_sentiment": "Positive | Negative | Neutral | Mixed",
  "research_confidence": "High | Medium | Low",
  "tags": ["tag1", "tag2", "tag3"]
}}

Extract at least:
- 3 pain points, 2 motivations, 2 unmet needs, 2 JTBD statements
- 3 notable quotes, 3 follow-up questions, 3 PM actions
- Sentiment for every major topic discussed

Return ONLY the JSON."""


def _cross_prompt(insights_list: List[InterviewInsights]) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    summaries = []
    for ins in insights_list:
        pain_titles = [p.title for p in ins.pain_points]
        unmet_titles = [u.title for u in ins.unmet_needs]
        quotes = [q.quote[:100] for q in ins.notable_quotes[:3]]
        summaries.append(
            f"INTERVIEW {ins.interview_id} ({ins.participant_label}):\n"
            f"Summary: {ins.executive_summary}\n"
            f"Pain points: {', '.join(pain_titles)}\n"
            f"Unmet needs: {', '.join(unmet_titles)}\n"
            f"Key quotes: {' | '.join(quotes)}\n"
            f"Sentiment: {ins.overall_sentiment}\n"
            f"Tags: {', '.join(ins.tags)}"
        )

    return f"""Analyze these {len(insights_list)} interview summaries and identify cross-interview patterns.

{chr(10).join(summaries)}

Return a JSON object:
{{
  "total_interviews": {len(insights_list)},
  "interviews_analyzed": {json.dumps([i.interview_id for i in insights_list])},
  "generated_at": "{today}",
  "top_themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
  "patterns": [
    {{
      "pattern_title": "Short pattern name",
      "pattern_type": "pain_point | motivation | unmet_need | jtbd | sentiment",
      "description": "What this pattern reveals",
      "frequency": 3,
      "interview_ids": ["id1", "id2"],
      "supporting_quotes": ["quote1", "quote2"],
      "confidence": "High | Medium | Low",
      "pm_implication": "Specific product or research implication"
    }}
  ],
  "consensus_pain_points": ["pain shared across most interviews"],
  "divergent_findings": ["things that varied significantly between participants"],
  "recommended_next_research": ["specific follow-up research action"],
  "synthesis_narrative": "4-5 sentence narrative synthesizing what all these interviews tell us collectively about the user and the product opportunity"
}}

Identify at least 3 patterns. Return ONLY the JSON."""


def analyze_interview(
    transcript: str,
    participant_label: str,
    interview_id: str,
    source: str,
    api_key: str,
) -> InterviewInsights:
    if api_key == "DEMO":
        import time
        time.sleep(1.5) # Simulate slight thinking time
        today = datetime.now().strftime("%Y-%m-%d")
        
        is_dev = "developer" in participant_label.lower()
        
        if is_dev:
            demo_data = {
                "interview_id": interview_id,
                "participant_label": participant_label,
                "interview_date": today,
                "duration_minutes": 25,
                "transcript_source": source,
                "executive_summary": "The user is overwhelmed by the complexity of the current project management tool. They want a simplified, focused view of their daily coding tasks to avoid missing critical bugs.",
                "pain_points": [
                    {
                        "title": "Cluttered Interface",
                        "description": "Too many buttons and custom fields obscure their actual daily work.",
                        "frequency": "Dominant theme",
                        "severity": "High",
                        "confidence": "High",
                        "direct_quote": "I spend almost 20 minutes every morning just trying to figure out which sprint my active tickets are hidden in."
                    }
                ],
                "motivations": [
                    {
                        "title": "Focused Execution",
                        "description": "Wants to jump straight into coding without administrative overhead.",
                        "underlying_driver": "Professional productivity",
                        "confidence": "High"
                    }
                ],
                "unmet_needs": [
                    {
                        "title": "Daily Focus List",
                        "description": "Needs a distilled, prioritized list of what to code today.",
                        "current_workaround": "Physical sticky notes on the monitor",
                        "opportunity_size": "High",
                        "confidence": "High"
                    }
                ],
                "jtbd_statements": [
                    {
                        "situation": "logging into the system",
                        "motivation": "instantly see a prioritized list of my bugs",
                        "outcome": "start coding immediately without missing critical issues",
                        "full_statement": "When I log into the system, I want to instantly see a prioritized list of my bugs, so I can start coding immediately without missing critical issues."
                    }
                ],
                "persona_signals": [],
                "sentiment_map": [],
                "notable_quotes": [],
                "follow_up_questions": [],
                "pm_actions": [
                    {
                        "action": "Design a 'My Day' focused view",
                        "category": "Design",
                        "priority": "P1",
                        "rationale": "Users are resorting to physical sticky notes."
                    }
                ],
                "overall_sentiment": "Negative",
                "research_confidence": "High",
                "tags": ["Demo", "Developer", "UX Clutter"]
            }
        elif "marathon" in participant_label.lower():
            demo_data = {
                "interview_id": interview_id,
                "participant_label": participant_label,
                "interview_date": today,
                "duration_minutes": 45,
                "transcript_source": source,
                "executive_summary": "This marathon runner loves the accurate tracking but is deeply frustrated by battery drain during multi-hour runs. They might switch apps if this isn't fixed.",
                "pain_points": [{"title": "Severe Battery Drain", "description": "App kills phone battery during 3+ hour runs.", "frequency": "Dominant theme", "severity": "Critical", "confidence": "High", "direct_quote": "My phone died at mile 20. It's completely unacceptable."}],
                "motivations": [{"title": "Reliability", "description": "Needs the app to last the entire race.", "underlying_driver": "Peace of mind", "confidence": "High"}],
                "unmet_needs": [{"title": "Low Power Mode", "description": "An ultra-low battery mode for long events.", "current_workaround": "Carrying a heavy power bank", "opportunity_size": "High", "confidence": "High"}],
                "jtbd_statements": [{"situation": "running an ultra-marathon", "motivation": "ensure my phone stays alive", "outcome": "track my full race and have phone for emergencies", "full_statement": "When running an ultra-marathon, I want to ensure my phone stays alive, so I can track my full race and have phone for emergencies."}],
                "persona_signals": [], "sentiment_map": [], "notable_quotes": [], "follow_up_questions": [],
                "pm_actions": [{"action": "Investigate GPS polling frequency", "category": "Engineering", "priority": "P0", "rationale": "Critical risk of churn."}],
                "overall_sentiment": "Mixed", "research_confidence": "High", "tags": ["Demo", "Marathon", "Battery"]
            }
        elif "gym" in participant_label.lower():
            demo_data = {
                "interview_id": interview_id,
                "participant_label": participant_label,
                "interview_date": today,
                "duration_minutes": 20,
                "transcript_source": source,
                "executive_summary": "Casual gym goer finding the app too complex for simple weight logging. They just want a fast, simple spreadsheet-like interface.",
                "pain_points": [{"title": "Complex Navigation", "description": "Too many menus to log a simple workout.", "frequency": "Recurring", "severity": "Medium", "confidence": "High", "direct_quote": "I just want to log 3 sets of bench press, why does it take 5 clicks?"}],
                "motivations": [{"title": "Speed", "description": "Wants to log workouts quickly between sets.", "underlying_driver": "Convenience", "confidence": "High"}],
                "unmet_needs": [{"title": "Quick Entry View", "description": "A single-screen interface for fast data entry.", "current_workaround": "Using Apple Notes", "opportunity_size": "Medium", "confidence": "High"}],
                "jtbd_statements": [{"situation": "resting between sets", "motivation": "log my reps instantly", "outcome": "focus on my workout instead of my phone", "full_statement": "When resting between sets, I want to log my reps instantly, so I can focus on my workout instead of my phone."}],
                "persona_signals": [], "sentiment_map": [], "notable_quotes": [], "follow_up_questions": [],
                "pm_actions": [{"action": "Simplify default workout view", "category": "Design", "priority": "P2", "rationale": "Improve retention for casual users."}],
                "overall_sentiment": "Neutral", "research_confidence": "High", "tags": ["Demo", "Casual", "UI"]
            }
        elif "trainer" in participant_label.lower():
            demo_data = {
                "interview_id": interview_id,
                "participant_label": participant_label,
                "interview_date": today,
                "duration_minutes": 40,
                "transcript_source": source,
                "executive_summary": "Personal trainer managing multiple clients. Loves the data capture but needs a centralized dashboard to view all client progress at once.",
                "pain_points": [{"title": "No Client Overview", "description": "Has to log into each client's profile individually to see their data.", "frequency": "Dominant theme", "severity": "High", "confidence": "High", "direct_quote": "Checking on 15 clients takes me an hour because I have to open each profile one by one."}],
                "motivations": [{"title": "Efficiency", "description": "Wants to review all clients in under 15 minutes.", "underlying_driver": "Business scalability", "confidence": "High"}],
                "unmet_needs": [{"title": "Trainer Dashboard", "description": "A master view showing all clients' adherence.", "current_workaround": "Making clients text them screenshots", "opportunity_size": "High", "confidence": "High"}],
                "jtbd_statements": [{"situation": "starting my workday", "motivation": "see which clients missed their workouts", "outcome": "follow up with them immediately", "full_statement": "When starting my workday, I want to see which clients missed their workouts, so I can follow up with them immediately."}],
                "persona_signals": [], "sentiment_map": [], "notable_quotes": [], "follow_up_questions": [],
                "pm_actions": [{"action": "Research Coach/Trainer portal", "category": "Discovery", "priority": "P1", "rationale": "Unlocks a new B2B revenue stream."}],
                "overall_sentiment": "Positive", "research_confidence": "High", "tags": ["Demo", "Trainer", "B2B"]
            }
        else:
            demo_data = {
                "interview_id": interview_id,
                "participant_label": participant_label,
                "interview_date": today,
                "duration_minutes": 30,
                "transcript_source": source,
                "executive_summary": "The manager frequently struggles with resource allocation due to poor high-level visibility. They are forced to manually export data to Excel to calculate team bandwidth.",
                "pain_points": [
                    {
                        "title": "Poor Resource Visibility",
                        "description": "Cannot easily see team bandwidth or workload in the native tool.",
                        "frequency": "Dominant theme",
                        "severity": "High",
                        "confidence": "High",
                        "direct_quote": "I literally have to export our active sprint data into a giant Excel spreadsheet just to see who is overworked."
                    },
                    {
                        "title": "Manual Reporting",
                        "description": "Exporting data to Excel takes too much time (3 hours every Monday).",
                        "frequency": "Recurring",
                        "severity": "High",
                        "confidence": "High",
                        "direct_quote": "It takes me three hours of manual formatting every single Monday."
                    }
                ],
                "motivations": [
                    {
                        "title": "Preventing Burnout",
                        "description": "Wants to assign epics safely without overworking the team.",
                        "underlying_driver": "Team health and retention",
                        "confidence": "High"
                    }
                ],
                "unmet_needs": [
                    {
                        "title": "Automated Capacity Calculation",
                        "description": "Needs the software to calculate bandwidth based on story points automatically.",
                        "current_workaround": "Excel spreadsheets",
                        "opportunity_size": "High",
                        "confidence": "High"
                    }
                ],
                "jtbd_statements": [
                    {
                        "situation": "planning a new product release",
                        "motivation": "know exactly who is available",
                        "outcome": "assign large epics without burning my team out",
                        "full_statement": "When I am planning a new product release, I want to know exactly who is available, so I can assign large epics without burning my team out."
                    }
                ],
                "persona_signals": [],
                "sentiment_map": [],
                "notable_quotes": [],
                "follow_up_questions": [],
                "pm_actions": [
                    {
                        "action": "Design team capacity dashboard",
                        "category": "Roadmap",
                        "priority": "P0",
                        "rationale": "High severity pain point causing massive manual work."
                    }
                ],
                "overall_sentiment": "Mixed",
                "research_confidence": "High",
                "tags": ["Demo", "Manager", "Resource Planning"]
            }
        return InterviewInsights(**demo_data)

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _single_prompt(
            transcript, participant_label, interview_id, source
        )}],
    )
    raw   = msg.content[0].text
    clean = re.sub(r"```json|```", "", raw).strip()
    data  = json.loads(clean)

    # Inject duration estimate
    from transcriber import estimate_duration
    data["duration_minutes"] = estimate_duration(transcript)

    return InterviewInsights(**data)


def analyze_cross_patterns(
    insights_list: List[InterviewInsights],
    api_key: str,
) -> CrossInterviewReport:
    if api_key == "DEMO":
        import time
        time.sleep(1.5)
        demo_report = {
            "total_interviews": len(insights_list),
            "interviews_analyzed": [ins.participant_label for ins in insights_list],
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "top_themes": ["UI Clutter", "Navigation Friction", "Data Overwhelm"],
            "patterns": [
                {
                    "pattern_title": "UI Clutter and Overwhelm",
                    "pattern_type": "pain_point",
                    "description": "Users are spending too much time navigating menus rather than achieving their actual goals.",
                    "frequency": len(insights_list),
                    "interview_ids": [ins.interview_id for ins in insights_list],
                    "supporting_quotes": ["I spend 20 minutes a day just trying to figure out which sprint my tickets are in.", "I just want to log 3 sets of bench press, why does it take 5 clicks?"],
                    "confidence": "High",
                    "pm_implication": "Redesign default view to prioritize quick-add interactions."
                }
            ],
            "consensus_pain_points": [
                "Core navigation requires too many clicks.",
                "Lack of a high-level summary overview."
            ],
            "divergent_findings": [
                "Power users/Managers want highly detailed data exports, while End-users want faster, frictionless entry without metadata."
            ],
            "recommended_next_research": [
                "Conduct usability testing on a prototype of a single-screen 'Quick Add' dashboard."
            ],
            "synthesis_narrative": "Across these interviews, participants uniformly praised the core functionality but shared severe frustrations with the user experience and interface clutter. The data indicates a strong need to simplify workflows for casual users while preserving robust features for power users."
        }
        return CrossInterviewReport(**demo_report)

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _cross_prompt(insights_list)}],
    )
    raw   = msg.content[0].text
    clean = re.sub(r"```json|```", "", raw).strip()
    return CrossInterviewReport(**json.loads(clean))
