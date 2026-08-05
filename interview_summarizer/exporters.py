from __future__ import annotations
import io
import json
from schema import InterviewInsights, CrossInterviewReport

NAVY="#1F3C6B"; INDIGO="#4F46E5"; GREEN="#16A34A"
AMBER="#D97706"; RED="#DC2626"; LIGHT="#EEF2FF"
WHITE="#FFFFFF"; MUTED="#64748B"; DARK="#1E293B"

SEV_CLR = {"High": RED, "Medium": AMBER, "Low": GREEN}
SENT_CLR = {"Positive": GREEN, "Negative": RED, "Neutral": MUTED, "Mixed": AMBER}


# ── JSON ─────────────────────────────────────────────────────────────────────
def export_json(obj) -> str:
    return obj.model_dump_json(indent=2)


# ── PDF ──────────────────────────────────────────────────────────────────────
def export_pdf(ins: InterviewInsights) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, HRFlowable, PageBreak
    )
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm)

    def C(h): return colors.HexColor(h)

    t_s  = ParagraphStyle("T",  fontSize=18, textColor=C(NAVY),
                           fontName="Helvetica-Bold", spaceAfter=4, alignment=TA_CENTER)
    sub_s= ParagraphStyle("Su", fontSize=10, textColor=C(MUTED), spaceAfter=10, alignment=TA_CENTER)
    h2_s = ParagraphStyle("H2", fontSize=12, textColor=C(NAVY),
                           fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=5)
    h3_s = ParagraphStyle("H3", fontSize=10, textColor=C(INDIGO),
                           fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
    bd_s = ParagraphStyle("B",  fontSize=9,  textColor=C(DARK),
                           spaceAfter=4, leading=14, alignment=TA_JUSTIFY)
    q_s  = ParagraphStyle("Q",  fontSize=9,  textColor=C(INDIGO),
                           fontName="Helvetica-Oblique", spaceAfter=4,
                           leftIndent=12, leading=14)
    sm_s = ParagraphStyle("Sm", fontSize=8,  textColor=C(MUTED), spaceAfter=3)

    def hdr(text, fill=NAVY):
        t = Table([[Paragraph(text, ParagraphStyle("HT", fontSize=11,
                    textColor=colors.white, fontName="Helvetica-Bold"))]],
                  colWidths=[174*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),C(fill)),
            ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
            ("LEFTPADDING",(0,0),(-1,-1),10),
        ]))
        return t

    def badge_table(rows_data, col_widths):
        t = Table(rows_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),C(LIGHT)),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("GRID",(0,0),(-1,-1),0.5,C("#CBD5E1")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,C("#F8FAFC")]),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),5),("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        return t

    story = [
        Spacer(1,8*mm),
        Paragraph("User Interview Insights", t_s),
        Paragraph(f"{ins.participant_label}  ·  {ins.interview_date}  ·  Source: {ins.transcript_source}", sub_s),
        HRFlowable(width="100%", thickness=2, color=C(INDIGO)),
        Spacer(1,3*mm),
        Paragraph("Executive Summary", h2_s),
        Paragraph(ins.executive_summary, bd_s),
    ]

    # Sentiment + confidence strip
    sc_data = [["Overall Sentiment","Research Confidence","Duration","Interview ID"],
               [ins.overall_sentiment, ins.research_confidence,
                f"{ins.duration_minutes} min" if ins.duration_minutes else "—",
                ins.interview_id]]
    st = Table(sc_data, colWidths=[44*mm]*4)
    st.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C(LIGHT)),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),0.5,C("#CBD5E1")),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story += [Spacer(1,3*mm), st, PageBreak()]

    # Pain points
    story.append(hdr("🔴 Pain Points"))
    pp_rows = [["Title","Severity","Frequency","Confidence","Quote"]]
    for pp in ins.pain_points:
        pp_rows.append([pp.title, pp.severity, pp.frequency, pp.confidence,
                        f'"{pp.direct_quote[:80]}..."'])
    story += [Spacer(1,2*mm),
              badge_table(pp_rows,[42*mm,18*mm,28*mm,20*mm,66*mm]),
              Spacer(1,4*mm)]

    # Motivations
    story.append(hdr("💡 Motivations", INDIGO))
    for m in ins.motivations:
        story += [Paragraph(f"• {m.title}", h3_s),
                  Paragraph(m.description, bd_s),
                  Paragraph(f"Root driver: {m.underlying_driver}", sm_s)]

    # Unmet needs
    story += [Spacer(1,3*mm), hdr("🎯 Unmet Needs", "#0F766E")]
    un_rows = [["Need","Workaround","Opportunity","Confidence"]]
    for u in ins.unmet_needs:
        un_rows.append([u.title, u.current_workaround,
                        u.opportunity_size, u.confidence])
    story += [Spacer(1,2*mm),
              badge_table(un_rows,[50*mm,50*mm,24*mm,20*mm]),
              Spacer(1,3*mm), PageBreak()]

    # JTBD
    story.append(hdr("⚡ Jobs to Be Done"))
    for jt in ins.jtbd_statements:
        story += [Paragraph(jt.full_statement, q_s)]

    # Notable quotes
    story += [Spacer(1,4*mm), hdr("💬 Notable Quotes", "#7C3AED")]
    for nq in ins.notable_quotes:
        story += [Paragraph(f'"{nq.quote}"', q_s),
                  Paragraph(f"Context: {nq.context}  ·  Why it matters: {nq.significance}", sm_s)]

    story += [PageBreak()]

    # Follow-up questions
    story.append(hdr("❓ Follow-up Questions", AMBER.replace("#","")))
    for fq in ins.follow_up_questions:
        story += [Paragraph(f"[{fq.priority}] {fq.question}", h3_s),
                  Paragraph(fq.rationale, sm_s)]

    # PM Actions
    story += [Spacer(1,4*mm), hdr("⚡ PM Actions")]
    act_rows = [["Priority","Category","Action","Rationale"]]
    for a in ins.pm_actions:
        act_rows.append([a.priority, a.category, a.action, a.rationale])
    story += [Spacer(1,2*mm),
              badge_table(act_rows,[16*mm,22*mm,64*mm,72*mm])]

    doc.build(story)
    return buf.getvalue()


# ── Research Card (HTML) ──────────────────────────────────────────────────────
def export_research_card_html(ins: InterviewInsights) -> str:
    pain_html = "".join([
        f"""<div class="insight-item pain">
          <div class="item-title">{pp.title}
            <span class="badge sev-{pp.severity.lower()}">{pp.severity}</span>
          </div>
          <div class="item-desc">{pp.description}</div>
          <div class="item-quote">"{pp.direct_quote[:120]}..."</div>
        </div>""" for pp in ins.pain_points[:4]
    ])

    need_html = "".join([
        f"""<div class="insight-item need">
          <div class="item-title">{un.title}
            <span class="badge opp-{un.opportunity_size.lower()}">{un.opportunity_size} opportunity</span>
          </div>
          <div class="item-desc">Workaround: {un.current_workaround}</div>
        </div>""" for un in ins.unmet_needs[:3]
    ])

    jtbd_html = "".join([
        f'<div class="jtbd-item">"{jt.full_statement}"</div>'
        for jt in ins.jtbd_statements[:2]
    ])

    action_html = "".join([
        f"""<div class="action-item">
          <span class="badge prio-{a.priority.lower()}">{a.priority}</span>
          <span class="action-cat">{a.category}</span>
          {a.action}
        </div>""" for a in ins.pm_actions[:4]
    ])

    tags_html = "".join([f'<span class="tag">{t}</span>' for t in ins.tags])

    sent_color = {"Positive":"#16A34A","Negative":"#DC2626",
                  "Neutral":"#64748B","Mixed":"#D97706"}.get(ins.overall_sentiment,"#64748B")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Research Card — {ins.participant_label}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:system-ui,-apple-system,sans-serif;background:#F1F5F9;padding:24px}}
  .card{{background:white;border-radius:16px;max-width:900px;margin:0 auto;
         box-shadow:0 4px 24px rgba(0,0,0,0.08);overflow:hidden}}
  .card-header{{background:linear-gradient(135deg,#1F3C6B,#4F46E5);
                color:white;padding:24px 28px}}
  .card-header h1{{font-size:1.3rem;font-weight:700;margin-bottom:4px}}
  .card-header .meta{{font-size:.85rem;opacity:.75}}
  .sentiment-pill{{display:inline-block;background:rgba(255,255,255,.15);
                   color:white;padding:3px 12px;border-radius:20px;font-size:.8rem;
                   font-weight:600;margin-top:8px}}
  .card-body{{padding:24px 28px;display:grid;grid-template-columns:1fr 1fr;gap:20px}}
  .section{{margin-bottom:4px}}
  .section-title{{font-size:.75rem;font-weight:700;color:#64748B;
                  text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}}
  .insight-item{{padding:10px 12px;border-radius:8px;margin-bottom:8px;font-size:.85rem}}
  .insight-item.pain{{background:#FFF5F5;border-left:3px solid #EF4444}}
  .insight-item.need{{background:#EFF6FF;border-left:3px solid #3B82F6}}
  .item-title{{font-weight:600;color:#1E293B;margin-bottom:3px}}
  .item-desc{{color:#64748B;font-size:.82rem;margin-bottom:3px}}
  .item-quote{{color:#4F46E5;font-style:italic;font-size:.8rem}}
  .jtbd-item{{background:#EEF2FF;border-radius:8px;padding:10px 14px;
              font-size:.85rem;color:#1F3C6B;font-style:italic;margin-bottom:8px;
              border-left:3px solid #4F46E5}}
  .action-item{{padding:8px 12px;background:#F8FAFC;border-radius:6px;
                margin-bottom:6px;font-size:.83rem;border:1px solid #E2E8F0}}
  .action-cat{{color:#64748B;font-size:.75rem;margin:0 6px}}
  .badge{{display:inline-block;padding:2px 7px;border-radius:10px;
          font-size:.72rem;font-weight:700}}
  .sev-high{{background:#FEE2E2;color:#DC2626}}
  .sev-medium{{background:#FEF3C7;color:#D97706}}
  .sev-low{{background:#DCFCE7;color:#16A34A}}
  .opp-high{{background:#DCFCE7;color:#16A34A}}
  .opp-medium{{background:#FEF3C7;color:#D97706}}
  .opp-low{{background:#F1F5F9;color:#64748B}}
  .prio-p0{{background:#FEE2E2;color:#DC2626}}
  .prio-p1{{background:#FEF3C7;color:#D97706}}
  .prio-p2{{background:#EEF2FF;color:#4F46E5}}
  .tag{{background:#EEF2FF;color:#4F46E5;padding:3px 10px;border-radius:20px;
        font-size:.75rem;margin:2px;display:inline-block}}
  .summary-box{{grid-column:1/-1;background:#1F3C6B;color:white;
                border-radius:10px;padding:16px 20px;font-size:.9rem;line-height:1.7}}
  .full-width{{grid-column:1/-1}}
  .tags-row{{grid-column:1/-1;padding-top:4px}}
  .card-footer{{background:#F8FAFC;padding:14px 28px;font-size:.78rem;
                color:#94A3B8;border-top:1px solid #E2E8F0;text-align:center}}
</style>
</head>
<body>
<div class="card">
  <div class="card-header">
    <h1>🎙️ {ins.participant_label}</h1>
    <div class="meta">{ins.interview_date} · Source: {ins.transcript_source}
    {f'· {ins.duration_minutes} min' if ins.duration_minutes else ''} · ID: {ins.interview_id}</div>
    <div class="sentiment-pill" style="background:rgba(255,255,255,.15)">
      {ins.overall_sentiment} sentiment · {ins.research_confidence} confidence
    </div>
  </div>
  <div class="card-body">
    <div class="summary-box">{ins.executive_summary}</div>
    <div class="section">
      <div class="section-title">🔴 Pain Points</div>
      {pain_html}
    </div>
    <div class="section">
      <div class="section-title">🎯 Unmet Needs</div>
      {need_html}
    </div>
    <div class="full-width">
      <div class="section-title">⚡ Jobs to Be Done</div>
      {jtbd_html}
    </div>
    <div class="full-width">
      <div class="section-title">🗺️ PM Actions</div>
      {action_html}
    </div>
    <div class="tags-row">{tags_html}</div>
  </div>
  <div class="card-footer">
    Generated by PM User Research Engine · pm-user-research-engine
  </div>
</div>
</body>
</html>"""


# ── Notion ────────────────────────────────────────────────────────────────────
def push_to_notion(ins: InterviewInsights,
                   token: str, database_id: str) -> str:
    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    def para(text):
        return {"object":"block","type":"paragraph",
                "paragraph":{"rich_text":[{"text":{"content":str(text)[:2000]}}]}}
    def h2(text):
        return {"object":"block","type":"heading_2",
                "heading_2":{"rich_text":[{"text":{"content":text}}]}}
    def bullet(text):
        return {"object":"block","type":"bulleted_list_item",
                "bulleted_list_item":{"rich_text":[{"text":{"content":str(text)[:2000]}}]}}
    def divider():
        return {"object":"block","type":"divider","divider":{}}
    def quote(text):
        return {"object":"block","type":"quote",
                "quote":{"rich_text":[{"text":{"content":str(text)[:2000]}}]}}

    blocks = [
        para(f"Participant: {ins.participant_label} | Date: {ins.interview_date} | "
             f"Sentiment: {ins.overall_sentiment} | Confidence: {ins.research_confidence}"),
        divider(),
        h2("Executive Summary"), para(ins.executive_summary), divider(),
        h2("🔴 Pain Points"),
        *[bullet(f"[{p.severity}] {p.title}: {p.description}") for p in ins.pain_points],
        divider(), h2("💡 Motivations"),
        *[bullet(f"{m.title}: {m.description}") for m in ins.motivations],
        divider(), h2("🎯 Unmet Needs"),
        *[bullet(f"{u.title} (workaround: {u.current_workaround})") for u in ins.unmet_needs],
        divider(), h2("⚡ JTBD Statements"),
        *[quote(jt.full_statement) for jt in ins.jtbd_statements],
        divider(), h2("💬 Notable Quotes"),
        *[quote(f'"{nq.quote}" — {nq.context}') for nq in ins.notable_quotes],
        divider(), h2("❓ Follow-up Questions"),
        *[bullet(f"[{fq.priority}] {fq.question}") for fq in ins.follow_up_questions],
        divider(), h2("🗺️ PM Actions"),
        *[bullet(f"[{a.priority}] [{a.category}] {a.action}") for a in ins.pm_actions],
    ]

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {"title": [{"text": {"content":
                f"{ins.interview_id} — {ins.participant_label}"}}]},
        },
        "children": blocks[:100],   # Notion API limit per request
    }

    r = requests.post("https://api.notion.com/v1/pages",
                      headers=headers, json=payload)
    r.raise_for_status()
    return r.json().get("url", "Page created in Notion")
