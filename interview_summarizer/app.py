import streamlit as st
import json
import uuid
from datetime import datetime

st.set_page_config(
    page_title="Interview Transcript Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

.main, .stApp {
    background: radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(180, 101, 218, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(255, 154, 158, 0.1) 0%, transparent 50%);
    background-color: #F8F9FB;
    font-family: 'Inter', sans-serif;
}

[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(12px) !important;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08) !important;
}

/* Style input fields to have no outline, soft background, and glow on focus */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    border: none !important;
    background-color: rgba(255, 255, 255, 0.6) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.03) !important;
    transition: all 0.3s ease !important;
}
div[data-baseweb="input"]:focus-within > div, div[data-baseweb="select"]:focus-within > div {
    background-color: rgba(255, 255, 255, 1) !important;
    box-shadow: 0 8px 20px rgba(0, 242, 254, 0.2), inset 0 2px 4px rgba(0,0,0,0.01) !important;
    transform: translateY(-2px);
}


/* Segmented Control Panel Outline & Expansion */
[data-testid="stSegmentedControl"] {
    width: 100% !important;
}
[data-testid="stSegmentedControl"] > div {
    border: 1px solid #E5E7EB !important; /* Light grey outline */
    border-radius: 12px !important;
    background-color: white !important;
    padding: 4px !important;
    display: flex !important;
    width: 100% !important;
}
[data-testid="stSegmentedControl"] label,
[data-testid="stSegmentedControl"] button {
    flex: 1 1 100% !important;
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    min-height: 48px !important;
}

/* Inactive buttons text */
[data-testid="stSegmentedControl"] p {
    color: #6B7280 !important; /* Grey text for inactive */
    margin: 0 !important;
    text-align: center !important;
    font-weight: 500 !important;
}

/* Selected button styling */
[data-testid="stSegmentedControl"] [aria-checked="true"], 
[data-testid="stSegmentedControl"] [aria-selected="true"] {
    border: none !important;
    background: #EAF9E7 !important; /* Light green */
    box-shadow: none !important;
    border-radius: 8px !important;
}

[data-testid="stSegmentedControl"] [aria-checked="true"] p, 
[data-testid="stSegmentedControl"] [aria-selected="true"] p {
    color: #16A34A !important; /* Green font */
    font-weight: 700 !important;
}


.insight-card {
  border-radius: 16px; padding: 1.5rem; color: #111; background: white;
  margin: 0.8rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  transition: all 0.3s ease; border: 1px solid #F3F4F6;
}
.insight-card:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,0.06); }

.pain-card { border-left: 4px solid #FF4B4B; }
.motivation-card { border-left: 4px solid #3B82F6; }
.need-card { border-left: 4px solid #06B6D4; }
.jtbd-card { border-left: 4px solid #8B5CF6; font-style: italic; }
.quote-card { border-left: 4px solid #10B981; }
.action-card { border-left: 4px solid #F59E0B; }

.summary-box {
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  color: #1f2937;
  border-radius: 24px;
  padding: 2.2rem;
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.8;
  box-shadow: 0 10px 40px rgba(0,0,0,0.06), inset 0 2px 0 rgba(255,255,255,1);
  border: 1px solid rgba(255,255,255,0.8);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}
.summary-box::before {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 100%; height: 5px;
  background: linear-gradient(90deg, #00F2FE, #4FACFE, #00F2FE);
  background-size: 200% auto;
  animation: gradientFlow 3s linear infinite;
}
@keyframes gradientFlow {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
.summary-box:hover {
  transform: translateY(-5px) scale(1.01);
  box-shadow: 0 20px 50px rgba(0,198,251,0.15), inset 0 2px 0 rgba(255,255,255,1);
}
.summary-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}
.summary-icon {
  background: linear-gradient(135deg, #E0C3FC 0%, #8EC5FC 100%);
  border-radius: 14px;
  padding: 12px 16px;
  font-size: 1.5rem;
  margin-right: 15px;
  box-shadow: 0 4px 15px rgba(142, 197, 252, 0.4);
}
.summary-title {
  font-size: 1.4rem !important;
  font-weight: 800 !important;
  background: linear-gradient(to right, #111, #444);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 !important;
}
.summary-content {
  color: #4b5563;
  font-weight: 400;
}

.badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: .75rem; font-weight: 700; margin-right: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.badge-high { background: #FF4B4B; color: white; }
.badge-med { background: #FFA421; color: white; }
.badge-low { background: #00C073; color: white; }
.badge-p0 { background: #FF4B4B; color: white; box-shadow: 0 2px 4px rgba(255, 75, 75, 0.4); }
.badge-p1 { background: #FFA421; color: white; box-shadow: 0 2px 4px rgba(255, 164, 33, 0.4); }
.badge-p2 { background: #00C073; color: white; box-shadow: 0 2px 4px rgba(0, 192, 115, 0.4); }

.pattern-card {
  background: white; border-radius: 20px; padding: 1.5rem; border: none;
  margin: .8rem 0; box-shadow: 0 10px 20px rgba(0,0,0,0.05); transition: all 0.3s ease;
}
.pattern-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.08); }

.stButton>button {
  background: #EAF9E7; color: #16A34A; border: 1px solid #22C55E; border-radius: 12px; font-weight: 600;
  padding: 0.6rem 1.2rem; transition: all 0.3s ease; box-shadow: none;
}
.stButton>button:hover { background: #22C55E; color: white; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(34,197,94,0.2); }
.stButton>button:active { transform: translateY(1px); box-shadow: none; }

h1 { color: #111111 !important; font-weight: 800; letter-spacing: -1px; }
h2 { color: #222222 !important; font-weight: 700; }
h3 { color: #333333 !important; font-weight: 600; }

.score-cards-container {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}
.score-card {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.score-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0,0,0,0.1);
}
.score-item {
  text-align: center;
}
.score-label {
  color: #64748B;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}
.score-value {
  color: #111111;
  font-size: 2.5rem;
  font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎙️ Interview Transcript Summarizer")
st.caption("Transforms raw interview transcripts into structured research insights — pain points, motivations, JTBD, quotes, follow-up questions, and PM actions.")

st.markdown("""<div style='font-size:.85rem;color:#64748B;margin-bottom:1rem'>
Part of PM User Research Engine — <a href='https://github.com/suriyaethiraj/pm-user-research-engine' style='color:#4F46E5;text-decoration:none;font-weight:600'>GitHub ↗</a>
</div>""", unsafe_allow_html=True)

settings_col, _ = st.columns([1, 2])
with settings_col:
    with st.expander("Settings", expanded=True):
        st.markdown("Please provide your API keys to use the tools below.")
        llm_choice = st.selectbox("Select LLM Provider", ["Anthropic", "Gemini", "Groq", "Demo Data"])
        
        if llm_choice == "Demo Data":
            api_key = "DEMO"
            gemini_key, groq_key, openai_key = "", "", ""
            st.info("💡 Demo Mode Active! Real data will be pre-filled, and analysis runs instantly without an API key.")
        elif llm_choice == "Anthropic":
            api_key = st.text_input("Anthropic API Key", type="password")
            gemini_key, groq_key = "", ""
        elif llm_choice == "Gemini":
            gemini_key = st.text_input("Gemini API Key", type="password")
            api_key, groq_key = "", ""
        elif llm_choice == "Groq":
            groq_key = st.text_input("Groq API Key", type="password")
            api_key, gemini_key = "", ""
                
        if llm_choice != "Demo Data":
            openai_key = st.text_input("OpenAI API Key (audio)", type="password", help="Required for audio transcription via Whisper")

st.markdown("---")

# ── Session state ─────────────────────────────────────────────────────────────
if "interviews" not in st.session_state:
    st.session_state["interviews"] = {}   # id → InterviewInsights

# ── Tabs ──────────────────────────────────────────────────────────────────────
nav_col, _ = st.columns([3, 1])
with nav_col:
    nav_selection = st.segmented_control(
        "**Interview Types**",
        ["🎤 Single Interview", "⚖️ Compare Two", "📦 Batch Mode", "🔍 Pattern Finder", "📚 Library"],
        default="🎤 Single Interview",
        label_visibility="visible"
    )

st.markdown("""
<style>
.stApp, .main {
    background-color: #F8F9FA !important;
    background-image: none !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if nav_selection == "🎤 Single Interview":
    st.subheader("Analyze a Single Interview")

    c1, c2 = st.columns(2)
    default_p = "Shopper - Frequent Online Buyer" if api_key == "DEMO" else ""
    participant = c1.text_input("Participant label *", value=default_p,
                                placeholder="P1 — Senior PM at Series B startup, 5 yrs exp")
    interview_id = c2.text_input("Interview ID", value=f"INT-{datetime.now().strftime('%Y%m%d')}-001")

    input_method = st.segmented_control("Inputs", ["Paste text", "Upload audio",
                                              "Upload PDF", "Upload DOCX"],
                             default="Paste text")

    transcript_text = ""
    source_label = "text"

    if input_method == "Paste text":
        default_t = "Interviewer: Walk me through your most recent experience trying to buy something on our website.\nParticipant: I was trying to buy a pair of running shoes last week. I found the shoes quickly, added them to my cart, and went to checkout. But right when I clicked checkout, a giant pop-up forced me to create a full account with a password and email verification before I could even see the shipping costs." if api_key == "DEMO" else ""
        transcript_text = st.text_area("Paste transcript here *", height=220, value=default_t,
            placeholder="Interviewer: Tell me about your current workflow...\nParticipant: So the biggest problem I have is...")
        source_label = "text"

    elif input_method == "Upload audio":
        audio_file = st.file_uploader("Upload audio (mp3, mp4, wav, m4a, webm)",
                                       type=["mp3","mp4","wav","m4a","webm","ogg"])
        if audio_file:
            st.audio(audio_file)
            if st.button("📝 Transcribe Audio First"):
                if not openai_key:
                    st.error("OpenAI API key required for Whisper transcription.")
                else:
                    with st.spinner("🎙️ Whisper is transcribing…"):
                        from transcriber import transcribe_audio, clean_transcript
                        raw_t, src = transcribe_audio(
                            audio_file.read(), audio_file.name, openai_key
                        )
                        transcript_text = clean_transcript(raw_t)
                        st.session_state["current_transcript"] = transcript_text
                        source_label = src
                        st.success("✅ Transcription complete!")
            transcript_text = st.session_state.get("current_transcript", "")
            if transcript_text:
                st.text_area("Transcript preview", transcript_text[:1000]+"…",
                             height=120, disabled=True)
            source_label = "audio_whisper"

    elif input_method == "Upload PDF":
        pdf_file = st.file_uploader("Upload PDF transcript", type=["pdf"])
        if pdf_file:
            with st.spinner("Extracting text…"):
                from transcriber import extract_pdf_text, clean_transcript
                transcript_text = clean_transcript(extract_pdf_text(pdf_file.read()))
                st.text_area("Extracted text preview", transcript_text[:800]+"…",
                             height=100, disabled=True)
        source_label = "pdf"

    elif input_method == "Upload DOCX":
        docx_file = st.file_uploader("Upload DOCX transcript", type=["docx","doc"])
        if docx_file:
            with st.spinner("Extracting text…"):
                from transcriber import extract_docx_text, clean_transcript
                transcript_text = clean_transcript(extract_docx_text(docx_file.read()))
                st.text_area("Extracted text preview", transcript_text[:800]+"…",
                             height=100, disabled=True)
        source_label = "docx"

    if st.button("🧠 Analyze Interview", use_container_width=True, key="btn_single"):
        if not api_key:
            st.error("Anthropic API key required."); st.stop()
        if not transcript_text.strip():
            st.error("Provide a transcript."); st.stop()
        if not participant.strip():
            st.error("Enter a participant label."); st.stop()

        with st.spinner("🔬 Claude is extracting insights…"):
            try:
                from analyzer import analyze_interview
                ins = analyze_interview(
                    transcript_text, participant,
                    interview_id, source_label, api_key
                )
                st.session_state["interviews"][interview_id] = ins
                st.session_state["current_insights"] = ins
                st.success("✅ Analysis complete!")
                st.balloons()
                st.toast('Insights generated successfully!', icon='🚀')
            except Exception as e:
                st.error(f"Analysis failed: {e}"); st.stop()

    # ── Display results ───────────────────────────────────────────────────────
    if "current_insights" in st.session_state:
        ins = st.session_state["current_insights"]
        from exporters import export_json, export_pdf, export_research_card_html

        st.markdown("---")
        st.subheader(f"📊 Insights: {ins.participant_label}")

        score_card_html = f"""
        <div class="score-cards-container">
            <div class="score-card">
                <div class="score-item">
                    <div class="score-label">Pain Points</div>
                    <div class="score-value">{len(ins.pain_points)}</div>
                </div>
            </div>
            <div class="score-card">
                <div class="score-item">
                    <div class="score-label">Unmet Needs</div>
                    <div class="score-value">{len(ins.unmet_needs)}</div>
                </div>
            </div>
            <div class="score-card">
                <div class="score-item">
                    <div class="score-label">JTBD Statements</div>
                    <div class="score-value">{len(ins.jtbd_statements)}</div>
                </div>
            </div>
            <div class="score-card">
                <div class="score-item">
                    <div class="score-label">PM Actions</div>
                    <div class="score-value">{len(ins.pm_actions)}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(score_card_html, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='summary-box'>
            <div class='summary-header'>
                <div class='summary-icon'>✨</div>
                <h3 class='summary-title'>Executive Summary</h3>
            </div>
            <div class='summary-content'>{ins.executive_summary}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**🔴 Pain Points**")
        for pp in ins.pain_points:
            sev_cls = {"High":"badge-high","Medium":"badge-med","Low":"badge-low"}.get(pp.severity,"badge-med")
            st.markdown(f"""<div class='insight-card pain-card'>
              <strong>{pp.title}</strong>
              <span class='badge {sev_cls}'>{pp.severity}</span>
              <span class='badge' style='background:#EEF2FF;color:#4F46E5'>{pp.frequency}</span><br>
              <span style='color:#64748B;font-size:.85rem'>{pp.description}</span><br>
              <em style='color:#4F46E5;font-size:.82rem'>"{pp.direct_quote[:100]}…"</em>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>**💡 Motivations**", unsafe_allow_html=True)
        for m in ins.motivations:
            st.markdown(f"""<div class='insight-card motivation-card'>
              <strong>{m.title}</strong><br>
              <span style='color:#64748B;font-size:.85rem'>{m.description}</span><br>
              <span style='color:#4F46E5;font-size:.82rem'>Root: {m.underlying_driver}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>**🎯 Unmet Needs**", unsafe_allow_html=True)
        for un in ins.unmet_needs:
            opp_cls = {"High":"badge-low","Medium":"badge-med","Low":"badge-high"}.get(un.opportunity_size,"badge-med")
            st.markdown(f"""<div class='insight-card need-card'>
              <strong>{un.title}</strong>
              <span class='badge {opp_cls}'>{un.opportunity_size} opportunity</span><br>
              <span style='color:#64748B;font-size:.85rem'>{un.description}</span><br>
              <span style='font-size:.82rem'>🔧 Workaround: {un.current_workaround}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>**⚡ JTBD Statements**", unsafe_allow_html=True)
        for jt in ins.jtbd_statements:
            st.markdown(f"<div class='insight-card jtbd-card'>{jt.full_statement}</div>",
                        unsafe_allow_html=True)

        st.markdown("<br>**🗺️ PM Actions**", unsafe_allow_html=True)
        for a in ins.pm_actions:
            p_cls = {"P0":"badge-p0","P1":"badge-p1","P2":"badge-p2"}.get(a.priority,"badge-p2")
            st.markdown(f"""<div class='insight-card action-card'>
              <span class='badge {p_cls}'>{a.priority}</span>
              <span style='color:#64748B;font-size:.78rem'>{a.category}</span><br>
              <strong style='font-size:.88rem'>{a.action}</strong><br>
              <span style='color:#64748B;font-size:.82rem'>{a.rationale}</span>
            </div>""", unsafe_allow_html=True)

        if ins.notable_quotes:
            st.markdown("<br>**💬 Notable Quotes**", unsafe_allow_html=True)
            qc = st.columns(min(len(ins.notable_quotes), 3))
            for i, nq in enumerate(ins.notable_quotes[:3]):
                with qc[i]:
                    st.markdown(f"""<div class='insight-card quote-card'>
                      <em>"{nq.quote[:180]}"</em><br>
                      <span style='color:#64748B;font-size:.8rem'>{nq.context}</span><br>
                      <span style='color:#0F766E;font-size:.8rem'>→ {nq.significance[:100]}</span>
                    </div>""", unsafe_allow_html=True)

        # Sentiment map
        if ins.sentiment_map:
            st.markdown("<br>**😊 Sentiment Map**", unsafe_allow_html=True)
            sent_cols = st.columns(min(len(ins.sentiment_map), 4))
            for i, sm in enumerate(ins.sentiment_map[:4]):
                with sent_cols[i % 4]:
                    clr = {"Positive":"#16A34A","Negative":"#DC2626",
                           "Neutral":"#64748B","Mixed":"#D97706"}.get(sm.sentiment,"#64748B")
                    st.markdown(f"""<div class='insight-card' style='border-left:4px solid {clr}'>
                      <strong style='font-size:.85rem'>{sm.topic}</strong><br>
                      <span style='color:{clr};font-weight:600;font-size:.82rem'>{sm.sentiment} · {sm.intensity}</span>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<br>**❓ Follow-up Questions**", unsafe_allow_html=True)
        for fq in ins.follow_up_questions:
            prio_clr = "#DC2626" if "Must" in fq.priority else "#D97706"
            st.markdown(f"""<div class='insight-card'>
              <span style='color:{prio_clr};font-weight:700;font-size:.8rem'>{fq.priority}</span><br>
              <strong style='font-size:.88rem'>{fq.question}</strong><br>
              <span style='color:#64748B;font-size:.82rem'>{fq.rationale}</span>
            </div>""", unsafe_allow_html=True)

        # Persona signals
        if ins.persona_signals:
            st.markdown("**👤 Persona Signals**")
            ps_cols = st.columns(min(len(ins.persona_signals), 3))
            for i, ps in enumerate(ins.persona_signals[:3]):
                with ps_cols[i % 3]:
                    st.markdown(f"""<div class='insight-card'>
                      <strong style='font-size:.85rem'>{ps.dimension}</strong><br>
                      <span style='color:#4F46E5;font-weight:600'>{ps.observed_value}</span><br>
                      <span style='color:#64748B;font-size:.8rem'>{ps.evidence[:100]}</span>
                    </div>""", unsafe_allow_html=True)

        # Tags
        tags_html = "".join([
            f'<span style="background:#EEF2FF;color:#4F46E5;padding:3px 10px;'
            f'border-radius:20px;font-size:.78rem;margin:2px;display:inline-block">{t}</span>'
            for t in ins.tags
        ])
        st.markdown(f"<br>{tags_html}", unsafe_allow_html=True)

        # Exports
        st.markdown("---")
        st.subheader("⬇️ Export")
        ex1,ex2,ex3 = st.columns(3)

        with ex1:
            st.download_button("📄 JSON", export_json(ins),
                file_name=f"interview_{ins.interview_id}.json",
                mime="application/json", use_container_width=True)
        with ex2:
            if st.button("📑 PDF", use_container_width=True, key="pdf_single"):
                with st.spinner("Building PDF…"):
                    try:
                        pdf = export_pdf(ins)
                        st.download_button("⬇️ Download PDF", pdf,
                            file_name=f"interview_{ins.interview_id}.pdf",
                            mime="application/pdf", use_container_width=True)
                    except Exception as ex: st.error(f"PDF failed: {ex}")
        with ex3:
            card_html = export_research_card_html(ins)
            st.download_button("🃏 Research Card", card_html,
                file_name=f"research_card_{ins.interview_id}.html",
                mime="text/html", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# BATCH MODE
# ══════════════════════════════════════════════════════════════════════════════
elif nav_selection == "📦 Batch Mode":
    st.subheader("📦 Analyze Multiple Interviews")
    st.info("Upload multiple transcript text files (.txt) — one per interview. Each file name becomes the participant label.")

    batch_files = st.file_uploader("Upload transcript files",
                                    type=["txt"], accept_multiple_files=True)
    
    run_batch = False
    is_demo = False
    
    if api_key == "DEMO":
        st.markdown("### Demo Mode Inputs")
        st.info("No files needed! I've pre-loaded 3 sample fitness app transcripts for this demo.")
        if st.button("🚀 Run Demo Batch Analysis", use_container_width=True):
            run_batch = True
            is_demo = True
    else:
        if batch_files and st.button("🚀 Run Batch Analysis", use_container_width=True):
            run_batch = True
            
    if run_batch:
        if not api_key:
            st.error("Anthropic API key required."); st.stop()
        progress = st.progress(0, text="Starting…")
        
        demo_files = [
            {"name": "P1_Marathon_Runner", "text": "I run marathons, so I'm tracking very long sessions. My biggest issue is that the app drains my battery incredibly fast."},
            {"name": "P2_Casual_Gym_Goer", "text": "I just want to log my weights and reps. Right now, I have to navigate through three menus just to find the basic workout log."},
            {"name": "P3_Personal_Trainer", "text": "I recommend it to all my clients to track their meals and workouts. But my massive pain point is that I can't easily see their data."}
        ]
        
        loop_items = demo_files if is_demo else batch_files
        
        for i, f in enumerate(loop_items):
            if is_demo:
                label = f["name"]
                text = f["text"]
            else:
                label = f.name.replace(".txt","")
                text = f.read().decode("utf-8", errors="ignore")
                
            iid   = f"BATCH-{i+1:03d}"
            progress.progress((i)/len(loop_items), text=f"Analyzing {label}…")
            try:
                from analyzer import analyze_interview
                ins = analyze_interview(text, label, iid, "text", api_key)
                st.session_state["interviews"][iid] = ins
                st.success(f"✅ {label} — {len(ins.pain_points)} pain points, {len(ins.pm_actions)} actions")
                
                # Show immediate mini-summary
                with st.expander(f"View Summary: {label}"):
                    st.markdown(f"""
                    <div class='insight-card' style='border-left: 4px solid #3B82F6;'>
                        <strong>Overall Sentiment</strong><br>
                        <span style='color: #4B5563;'>{ins.overall_sentiment}</span><br><br>
                        <strong>Research Confidence</strong><br>
                        <span style='color: #4B5563;'>{ins.research_confidence}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class='insight-card' style='border-left: 4px solid #10B981;'>
                        <strong>Executive Summary</strong><br>
                        <span style='color: #4B5563; font-size: 0.9rem;'>{ins.executive_summary}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("**🔴 Top Pain Points**")
                    for pp in ins.pain_points[:3]:
                        sev_cls = {"High":"badge-high","Medium":"badge-med","Low":"badge-low"}.get(pp.severity,"badge-med")
                        st.markdown(f"""<div class='insight-card pain-card' style='padding: 1rem;'>
                          <strong style='font-size: 0.95rem;'>{pp.title}</strong>
                          <span class='badge {sev_cls}'>{pp.severity}</span><br>
                          <span style='color:#64748B;font-size:.85rem'>{pp.description}</span>
                        </div>""", unsafe_allow_html=True)

                    st.markdown("**🎯 Top Unmet Needs**")
                    for un in ins.unmet_needs[:2]:
                        st.markdown(f"""<div class='insight-card need-card' style='padding: 1rem;'>
                          <strong style='font-size: 0.95rem;'>{un.title}</strong><br>
                          <span style='color:#64748B;font-size:.85rem'>{un.description}</span>
                        </div>""", unsafe_allow_html=True)
                        
                    st.markdown("**⚡ Core JTBD**")
                    for jt in ins.jtbd_statements[:1]:
                        st.markdown(f"<div class='insight-card jtbd-card' style='padding: 1rem; font-size: 0.9rem;'>{jt.full_statement}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed for {label}: {e}")
        progress.progress(1.0, text="Batch complete!")
        st.success(f"✅ {len(loop_items)} interviews analyzed and added to library.")
        st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE TWO
# ══════════════════════════════════════════════════════════════════════════════
elif nav_selection == "⚖️ Compare Two":
    st.subheader("⚖️ Compare Two Interviews Side by Side")
    library = st.session_state.get("interviews", {})
    
    if "cmp_mode_val" not in st.session_state:
        st.session_state.cmp_mode_val = "Choose from Library"

    if "force_cmp_mode" in st.session_state:
        st.session_state.cmp_mode_val = st.session_state.force_cmp_mode
        del st.session_state.force_cmp_mode

    opts = ["Choose from Library", "Input New Transcripts"]
    idx = opts.index(st.session_state.cmp_mode_val) if st.session_state.cmp_mode_val in opts else 0
    cmp_mode = st.radio("Select Comparison Source", opts, horizontal=True, index=idx)
    st.session_state.cmp_mode_val = cmp_mode
    
    if cmp_mode == "Choose from Library":
        if len(library) < 2:
            st.info("Analyze at least 2 interviews first (or use the 'Input New Transcripts' option above).")
        else:
            ids = list(library.keys())
            c1, c2 = st.columns(2)
            id_a = c1.selectbox("Interview A", ids, key="cmp_a")
            id_b = c2.selectbox("Interview B", [i for i in ids if i != id_a], key="cmp_b")
            ins_a = library[id_a]; ins_b = library[id_b]
    
            st.markdown("---")
            ca, cb = st.columns(2)
    
            def render_mini(col, ins):
                col.markdown(f"### {ins.participant_label}")
                
                col.markdown(f"""
                <div class='insight-card' style='border-left: 4px solid #3B82F6;'>
                    <strong>Overall Sentiment</strong><br>
                    <span style='color: #4B5563;'>{ins.overall_sentiment}</span><br><br>
                    <strong>Research Confidence</strong><br>
                    <span style='color: #4B5563;'>{ins.research_confidence}</span>
                </div>
                """, unsafe_allow_html=True)
                
                col.markdown(f"""
                <div class='insight-card' style='border-left: 4px solid #10B981;'>
                    <strong>Executive Summary</strong><br>
                    <span style='color: #4B5563; font-size: 0.9rem;'>{ins.executive_summary}</span>
                </div>
                """, unsafe_allow_html=True)

                col.markdown("**🔴 Top Pain Points**")
                for pp in ins.pain_points[:3]:
                    sev_cls = {"High":"badge-high","Medium":"badge-med","Low":"badge-low"}.get(pp.severity,"badge-med")
                    col.markdown(f"""<div class='insight-card pain-card' style='padding: 1rem;'>
                      <strong style='font-size: 0.95rem;'>{pp.title}</strong>
                      <span class='badge {sev_cls}'>{pp.severity}</span><br>
                      <span style='color:#64748B;font-size:.85rem'>{pp.description}</span>
                    </div>""", unsafe_allow_html=True)

                col.markdown("**🎯 Top Unmet Needs**")
                for un in ins.unmet_needs[:2]:
                    col.markdown(f"""<div class='insight-card need-card' style='padding: 1rem;'>
                      <strong style='font-size: 0.95rem;'>{un.title}</strong><br>
                      <span style='color:#64748B;font-size:.85rem'>{un.description}</span>
                    </div>""", unsafe_allow_html=True)

                col.markdown("**⚡ Core JTBD**")
                for jt in ins.jtbd_statements[:1]:
                    col.markdown(f"<div class='insight-card jtbd-card' style='padding: 1rem; font-size: 0.9rem;'>{jt.full_statement}</div>", unsafe_allow_html=True)
    
            render_mini(ca, ins_a); render_mini(cb, ins_b)
            
    else:
        st.markdown("Paste two interviews below to analyze and compare them instantly.")
        colA, colB = st.columns(2)
        
        with colA:
            st.markdown("#### Interview A")
            def_pa = "P1 - Junior Developer (Remote)" if api_key == "DEMO" else ""
            def_ta = "Interviewer: Thanks for joining! How do you currently manage your daily tasks?\nParticipant: It's honestly a bit overwhelming right now. Our team uses Jira, but the interface has way too many buttons, custom fields, and tabs." if api_key == "DEMO" else ""
            part_a = st.text_input("Participant A label", value=def_pa, placeholder="e.g. P1 - Junior PM", key="part_a_new")
            text_a = st.text_area("Paste Transcript A", value=def_ta, height=180, key="txt_a")
            
        with colB:
            st.markdown("#### Interview B")
            def_pb = "P2 - Engineering Manager (Remote)" if api_key == "DEMO" else ""
            def_tb = "Interviewer: How do you feel about the current project management tools your team is using?\nParticipant: They are technically powerful, but my absolute biggest frustration is getting a high-level view of my team's bandwidth." if api_key == "DEMO" else ""
            part_b = st.text_input("Participant B label", value=def_pb, placeholder="e.g. P2 - Senior PM", key="part_b_new")
            text_b = st.text_area("Paste Transcript B", value=def_tb, height=180, key="txt_b")
            
        if st.button("⚖️ Analyze & Compare", use_container_width=True):
            if not api_key:
                st.error("API key required in Settings.")
            elif not text_a or not text_b:
                st.error("Please provide both transcripts.")
            elif not part_a or not part_b:
                st.error("Please provide both participant labels.")
            else:
                with st.spinner("Analyzing both interviews with Claude... this may take a moment."):
                    try:
                        from analyzer import analyze_interview
                        id_a = f"INT-A-{datetime.now().strftime('%H%M%S')}"
                        ins_a = analyze_interview(text_a, part_a, id_a, "text", api_key)
                        st.session_state["interviews"][id_a] = ins_a
                        
                        id_b = f"INT-B-{datetime.now().strftime('%H%M%S')}"
                        ins_b = analyze_interview(text_b, part_b, id_b, "text", api_key)
                        st.session_state["interviews"][id_b] = ins_b
                        
                        # Automatically switch to library view and select the new transcripts
                        st.session_state.force_cmp_mode = "Choose from Library"
                        st.session_state.cmp_a = id_a
                        st.session_state.cmp_b = id_b
                        
                        st.success("Comparison complete! Both interviews have been added to your Library.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# CROSS-INTERVIEW PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif nav_selection == "🔍 Pattern Finder":
    st.subheader("🔍 Cross-Interview Pattern Finder")
    library = st.session_state.get("interviews", {})
    if len(library) < 2:
        st.info("Analyze at least 2 interviews to find patterns.")
    else:
        available = list(library.keys())
        selected  = st.multiselect("Select interviews to analyze",
                                    available, default=available)
        if len(selected) >= 2 and st.button("🔍 Find Patterns", use_container_width=True):
            if not api_key:
                st.error("API key required."); st.stop()
            with st.spinner("🧠 Claude is synthesizing patterns across interviews…"):
                try:
                    from analyzer import analyze_cross_patterns
                    pattern_report = analyze_cross_patterns(
                        [library[i] for i in selected], api_key
                    )
                    st.session_state["pattern_report"] = pattern_report
                    st.success("✅ Pattern analysis complete!")
                    st.snow()
                    st.toast('Patterns synthesized successfully!', icon='🔍')
                except Exception as e:
                    st.error(f"Pattern analysis failed: {e}")

        if "pattern_report" in st.session_state:
            pr = st.session_state["pattern_report"]
            st.markdown(f"""
            <div class='summary-box'>
                <div class='summary-header'>
                    <div class='summary-icon'>🧠</div>
                    <h3 class='summary-title'>Synthesis</h3>
                </div>
                <div class='summary-content'>{pr.synthesis_narrative}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**🏷️ Top Themes**")
            tags_html = "".join([
                f'<span style="background:#EEF2FF;color:#4F46E5;padding:4px 12px;'
                f'border-radius:20px;font-size:.82rem;margin:3px;display:inline-block">{t}</span>'
                for t in pr.top_themes
            ])
            st.markdown(tags_html, unsafe_allow_html=True)

            st.markdown("<br>**📊 Patterns**", unsafe_allow_html=True)
            for pat in pr.patterns:
                conf_clr = {"High":"#16A34A","Medium":"#D97706","Low":"#DC2626"}.get(pat.confidence,"#64748B")
                st.markdown(f"""<div class='pattern-card'>
                  <strong>{pat.pattern_title}</strong>
                  <span style='background:#EEF2FF;color:#4F46E5;padding:2px 8px;border-radius:10px;
                    font-size:.75rem;margin-left:6px'>{pat.pattern_type}</span>
                  <span style='color:{conf_clr};font-weight:600;font-size:.78rem;margin-left:6px'>
                    {pat.confidence} confidence · {pat.frequency} interviews</span><br>
                  <span style='color:#475569;font-size:.88rem'>{pat.description}</span><br>
                  <span style='color:#4F46E5;font-size:.85rem'>→ {pat.pm_implication}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>**✅ Consensus Pain Points**", unsafe_allow_html=True)
            for c in pr.consensus_pain_points:
                st.markdown(f"""<div class='insight-card pain-card' style='padding: 1rem;'>
                  <span style='color:#64748B;font-size:.9rem'>{c}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>**⚡ Recommended Next Research**", unsafe_allow_html=True)
            for r in pr.recommended_next_research:
                st.markdown(f"""<div class='insight-card action-card' style='padding: 1rem;'>
                  <span style='color:#64748B;font-size:.9rem'>{r}</span>
                </div>""", unsafe_allow_html=True)

            if pr.divergent_findings:
                st.markdown("<br>**🔀 Divergent Findings**", unsafe_allow_html=True)
                for d in pr.divergent_findings:
                    st.markdown(f"""<div class='insight-card need-card' style='padding: 1rem;'>
                      <span style='color:#64748B;font-size:.9rem'>{d}</span>
                    </div>""", unsafe_allow_html=True)

            from exporters import export_json
            st.download_button("📄 Export Patterns JSON",
                export_json(pr),
                file_name="cross_interview_patterns.json",
                mime="application/json")


# ══════════════════════════════════════════════════════════════════════════════
# LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
elif nav_selection == "📚 Library":
    st.subheader("📚 Interview Library")
    library = st.session_state.get("interviews", {})
    if not library:
        st.info("No interviews analyzed yet. Use Single or Batch mode.")
    else:
        st.markdown(f"**{len(library)} interviews in session**")
        for iid, ins in library.items():
            with st.expander(f"📋 {ins.interview_id} — {ins.participant_label}  ·  {ins.overall_sentiment}"):
                st.markdown(ins.executive_summary)
                col1,col2,col3 = st.columns(3)
                col1.metric("Pain Points",  len(ins.pain_points))
                col2.metric("Unmet Needs",  len(ins.unmet_needs))
                col3.metric("PM Actions",   len(ins.pm_actions))
                if st.button(f"Load this interview", key=f"load_{iid}"):
                    st.session_state["current_insights"] = ins
                    st.success(f"Loaded {iid} — switch to Single Interview tab to view.")
        st.markdown("---")
        all_json = json.dumps(
            {iid: json.loads(ins.model_dump_json()) for iid, ins in library.items()},
            indent=2
        )
        st.download_button("📥 Export All Interviews (JSON)", all_json,
            file_name="interview_library.json", mime="application/json")
