"""
Automated evaluation harness.
Run: python evals.py
"""
from __future__ import annotations
import os
from rich.console import Console
from rich.table import Table
from analyzer import analyze_interview, analyze_cross_patterns
from schema import InterviewInsights

console = Console()

SAMPLE_TRANSCRIPT_1 = """
Interviewer: Can you walk me through your typical day as a PM?

Participant: Sure. I spend the first hour just reading Slack and emails trying to figure out what's on fire. It's exhausting. I never get to actual strategic work before 11am.

Interviewer: What takes up most of your time?

Participant: Writing Jira tickets honestly. I probably spend 2 hours a day just translating requirements into stories. It feels like the most un-leveraged work I do. I keep thinking there has to be a better way.

Interviewer: What would an ideal solution look like?

Participant: Honestly? If I could just describe what I want in plain English and it becomes a proper ticket with acceptance criteria, I'd save so much time. I tried using GPT but it doesn't understand our Jira setup or our team's conventions.

Interviewer: How do you currently handle prioritization?

Participant: We have a spreadsheet that nobody trusts. Every stakeholder thinks their thing is the most important. The loudest person in the room usually wins and it drives me crazy.
"""

SAMPLE_TRANSCRIPT_2 = """
Interviewer: What are your biggest frustrations as a PM?

Participant: Writing user stories is killing me. I spend probably 3 hours a day on it. By the time I've written everything up properly, I've lost the thread of what I was actually trying to build.

Interviewer: Tell me more about that.

Participant: The context switching is brutal. I'll be in discovery, get an insight, and then by the time I've done all the admin work to document it, I've forgotten the nuance. There should be a way to capture the raw insight and have it auto-structured.

Interviewer: What tools do you use?

Participant: Jira for tickets, Confluence for docs, Notion for my personal notes. It's three different systems and nothing talks to each other. I copy-paste between them constantly.

Interviewer: What would make your job significantly better?

Participant: An AI that understood our product context, our team conventions, and could just take my stream-of-consciousness notes and turn them into proper documentation. That would be huge.
"""

TEST_CASES = [
    {"id": "eval_01", "label": "PM Workflow Pain", "transcript": SAMPLE_TRANSCRIPT_1, "participant": "P1 — Senior PM, Series B"},
    {"id": "eval_02", "label": "Documentation Pain", "transcript": SAMPLE_TRANSCRIPT_2, "participant": "P2 — PM, Enterprise SaaS"},
]

def check_schema(ins: InterviewInsights) -> bool:
    return bool(ins.executive_summary and ins.pain_points and ins.pm_actions)

def check_pain_points(ins: InterviewInsights) -> bool:
    return len(ins.pain_points) >= 2 and all(p.direct_quote for p in ins.pain_points)

def check_jtbd(ins: InterviewInsights) -> bool:
    return len(ins.jtbd_statements) >= 1 and all(
        "When I" in jt.full_statement for jt in ins.jtbd_statements
    )

def check_actions(ins: InterviewInsights) -> bool:
    return len(ins.pm_actions) >= 2 and all(
        a.priority in ["P0","P1","P2"] for a in ins.pm_actions
    )

def check_follow_ups(ins: InterviewInsights) -> bool:
    return len(ins.follow_up_questions) >= 2

def check_quotes_verbatim(ins: InterviewInsights) -> bool:
    return len(ins.notable_quotes) >= 2

def run_eval():
    api_key = os.environ.get("ANTHROPIC_API_KEY","")
    if not api_key:
        console.print("[red]Set ANTHROPIC_API_KEY.[/red]"); return

    table = Table(title="Interview Summarizer — Eval Benchmark", show_lines=True)
    table.add_column("ID",       style="cyan",  width=10)
    table.add_column("Label",    style="white", width=22)
    table.add_column("Schema",   justify="center", width=8)
    table.add_column("Pain pts", justify="center", width=9)
    table.add_column("JTBD",     justify="center", width=7)
    table.add_column("Actions",  justify="center", width=9)
    table.add_column("Follow-up",justify="center", width=10)
    table.add_column("Quotes",   justify="center", width=8)
    table.add_column("Status",   style="bold",  width=10)

    results = []
    stored  = []
    for tc in TEST_CASES:
        console.print(f"Running [cyan]{tc['id']}[/cyan]…")
        try:
            ins = analyze_interview(tc["transcript"], tc["participant"], tc["id"], "text", api_key)
            stored.append(ins)
            sc = check_schema(ins); pp = check_pain_points(ins)
            jb = check_jtbd(ins);   ac = check_actions(ins)
            fq = check_follow_ups(ins); qt = check_quotes_verbatim(ins)
            ok = all([sc,pp,jb,ac,fq,qt]); results.append(ok)
            table.add_row(tc["id"],tc["label"],
                "✅" if sc else "❌","✅" if pp else "❌","✅" if jb else "❌",
                "✅" if ac else "❌","✅" if fq else "❌","✅" if qt else "❌",
                "[green]PASS[/green]" if ok else "[yellow]REVIEW[/yellow]")
        except Exception as e:
            console.print(f"  [red]Error:[/red] {e}")
            table.add_row(tc["id"],tc["label"],"❌","❌","❌","❌","❌","❌","[red]FAIL[/red]")
            results.append(False)

    console.print(table)

    if len(stored) >= 2:
        console.print("\nRunning cross-interview pattern check…")
        try:
            pr = analyze_cross_patterns(stored, api_key)
            ok = len(pr.patterns) >= 2 and bool(pr.synthesis_narrative)
            console.print(f"Cross-pattern check: {'[green]PASS[/green]' if ok else '[red]FAIL[/red]'}")
        except Exception as e:
            console.print(f"[red]Cross-pattern failed: {e}[/red]")

    rate = sum(results)/len(results)*100 if results else 0
    console.print(f"\n[bold]Pass Rate:[/bold] {rate:.1f}%")

if __name__ == "__main__":
    run_eval()
