import re
from io import BytesIO
import streamlit as st

st.set_page_config(page_title="SkillBridge AI | Skill Gap Analyzer", page_icon="🎯", layout="wide")

ROLE_SKILLS = {
    "Backend Developer": {
        "Python": 1.0, "Java": 0.8, "SQL": 1.0, "REST API": 1.0, "Git": 0.7,
        "Authentication": 0.8, "Database Design": 0.8, "Testing": 0.7, "Docker": 0.5,
        "Data Structures": 0.8
    },
    "Frontend Developer": {
        "HTML": 0.8, "CSS": 0.8, "JavaScript": 1.0, "React": 1.0, "TypeScript": 0.7,
        "REST API": 0.6, "Git": 0.7, "Responsive Design": 0.7, "Testing": 0.5
    },
    "Full-Stack Developer": {
        "HTML": 0.6, "CSS": 0.6, "JavaScript": 1.0, "React": 0.8, "Python": 0.8,
        "REST API": 1.0, "SQL": 0.8, "Database Design": 0.8, "Git": 0.7, "Authentication": 0.7
    },
    "Data Analyst": {
        "SQL": 1.0, "Excel": 0.8, "Python": 0.8, "Pandas": 0.8, "Statistics": 0.8,
        "Power BI": 1.0, "Data Visualization": 0.8, "Tableau": 0.6
    },
    "Data Scientist": {
        "Python": 1.0, "SQL": 0.7, "Statistics": 1.0, "Pandas": 0.8, "NumPy": 0.7,
        "Machine Learning": 1.0, "Data Visualization": 0.6, "Scikit-learn": 0.8
    },
    "Machine Learning Engineer": {
        "Python": 1.0, "Machine Learning": 1.0, "Scikit-learn": 0.8, "PyTorch": 0.8,
        "TensorFlow": 0.8, "SQL": 0.5, "REST API": 0.7, "Docker": 0.7, "Git": 0.6
    },
    "Software Engineer": {
        "Data Structures": 1.0, "Algorithms": 1.0, "Python": 0.7, "Java": 0.7,
        "SQL": 0.6, "Git": 0.7, "OOP": 0.8, "Testing": 0.6, "REST API": 0.6
    },
}
ALIASES = {
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "rest api": ["rest api", "restful api", "api development", "apis"],
    "data structures": ["data structures", "dsa", "data structure"],
    "algorithms": ["algorithms", "algorithm design"],
    "machine learning": ["machine learning", "ml", "predictive modeling"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "power bi": ["power bi", "powerbi"],
    "data visualization": ["data visualization", "data visualisation", "visualization"],
    "database design": ["database design", "schema design", "database modeling"],
    "responsive design": ["responsive design", "responsive web design"],
    "oop": ["oop", "object-oriented programming", "object oriented programming"],
    "authentication": ["authentication", "jwt", "oauth", "authorization"],
}
RESOURCES = {
    "Python": ("Python Tutorial", "https://docs.python.org/3/tutorial/"),
    "Java": ("Dev.java Learning", "https://dev.java/learn/"),
    "SQL": ("SQLBolt interactive lessons", "https://sqlbolt.com/"),
    "REST API": ("MDN: HTTP and APIs", "https://developer.mozilla.org/en-US/docs/Web/HTTP"),
    "Git": ("Git documentation", "https://git-scm.com/doc"),
    "Authentication": ("OWASP Authentication Cheat Sheet", "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"),
    "Database Design": ("SQL normalization guide", "https://www.guru99.com/database-normalization.html"),
    "Testing": ("pytest documentation", "https://docs.pytest.org/"),
    "Docker": ("Docker Get Started", "https://docs.docker.com/get-started/"),
    "Data Structures": ("VisuAlgo", "https://visualgo.net/en"),
    "Algorithms": ("VisuAlgo", "https://visualgo.net/en"),
    "HTML": ("MDN HTML", "https://developer.mozilla.org/en-US/docs/Web/HTML"),
    "CSS": ("MDN CSS", "https://developer.mozilla.org/en-US/docs/Web/CSS"),
    "JavaScript": ("javascript.info", "https://javascript.info/"),
    "React": ("React Learn", "https://react.dev/learn"),
    "TypeScript": ("TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html"),
    "Responsive Design": ("web.dev Responsive Design", "https://web.dev/learn/design/"),
    "Excel": ("Microsoft Excel training", "https://support.microsoft.com/excel"),
    "Pandas": ("10 minutes to pandas", "https://pandas.pydata.org/docs/user_guide/10min.html"),
    "Statistics": ("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability"),
    "Power BI": ("Microsoft Learn: Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/"),
    "Tableau": ("Tableau free training", "https://www.tableau.com/learn/training"),
    "NumPy": ("NumPy Quickstart", "https://numpy.org/doc/stable/user/quickstart.html"),
    "Machine Learning": ("Google ML Crash Course", "https://developers.google.com/machine-learning/crash-course"),
    "Data Visualization": ("Data-to-Viz", "https://www.data-to-viz.com/"),
    "Scikit-learn": ("Scikit-learn tutorials", "https://scikit-learn.org/stable/tutorial/index.html"),
    "PyTorch": ("PyTorch Tutorials", "https://pytorch.org/tutorials/"),
    "TensorFlow": ("TensorFlow tutorials", "https://www.tensorflow.org/tutorials"),
    "OOP": ("Refactoring Guru: OOP", "https://refactoring.guru/design-patterns"),
}

def extract_text(uploaded):
    data = uploaded.getvalue()
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        try:
            import fitz
            doc = fitz.open(stream=data, filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception:
            try:
                from pypdf import PdfReader
                reader = PdfReader(BytesIO(data))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                raise ValueError("PDF read nahi hua. Scanned/image PDF ho sakta hai; DOCX ya text paste karke try karein.") from e
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    raise ValueError("Please upload a PDF, DOCX, or TXT file.")

def find_skills(text, skill_names):
    lower = re.sub(r"\s+", " ", text.lower())
    found = []
    for skill in skill_names:
        aliases = ALIASES.get(skill.lower(), [skill.lower()])
        for alias in aliases:
            pattern = r"(?<![a-z0-9+#])" + re.escape(alias) + r"(?![a-z0-9+#])"
            if re.search(pattern, lower):
                found.append(skill)
                break
    return found


def evidence_for_skill(text, skill):
    """Return up to two resume lines/sentences where a skill was detected."""
    aliases = ALIASES.get(skill.lower(), [skill.lower()])
    chunks = re.split(r"(?<=[.!?])\s+|[\n•]+", text)
    evidence = []
    for chunk in chunks:
        clean = re.sub(r"\s+", " ", chunk).strip(" -\t")
        low = clean.lower()
        if clean and any(re.search(r"(?<![a-z0-9+#])" + re.escape(alias) + r"(?![a-z0-9+#])", low) for alias in aliases):
            if clean not in evidence:
                evidence.append(clean[:260] + ("…" if len(clean) > 260 else ""))
        if len(evidence) >= 2:
            break
    return evidence


def build_pdf_report(report_lines, title="SkillBridge AI — Skill Gap Report"):
    """Create a downloadable PDF report in memory."""
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm, title=title)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SBTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=22, leading=27, textColor=colors.HexColor("#40358A"),
                              alignment=TA_LEFT, spaceAfter=7))
    styles.add(ParagraphStyle(name="SBBody", parent=styles["BodyText"], fontName="Helvetica",
                              fontSize=9.5, leading=14, textColor=colors.HexColor("#283044"), spaceAfter=5))
    styles.add(ParagraphStyle(name="SBSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=12, leading=16, textColor=colors.HexColor("#5143A6"),
                              spaceBefore=10, spaceAfter=5))
    story = [Paragraph("SkillBridge AI", styles["SBTitle"]),
             Paragraph(escape(title), styles["SBBody"]),
             HRFlowable(width="100%", thickness=1, color=colors.HexColor("#C8C1F5")), Spacer(1, 8)]
    section_heads = {"LEARNING RESOURCES:", "ROADMAP:", "SKILL BREAKDOWN:", "RECOMMENDED NEXT STEPS:"}
    for line in report_lines:
        clean = line.strip()
        if not clean:
            story.append(Spacer(1, 4))
        elif clean.upper() in section_heads:
            story.append(Paragraph(escape(clean), styles["SBSection"]))
        elif clean.startswith("- "):
            story.append(Paragraph("• " + escape(clean[2:]), styles["SBBody"]))
        else:
            story.append(Paragraph(escape(clean), styles["SBBody"]))
    doc.build(story)
    return buffer.getvalue()


def get_roadmap(missing):
    if not missing:
        return [
            ("Week 1", "Validate your skills with a small role-specific project and practice interview questions."),
            ("Week 2", "Improve your portfolio, test your work, and document measurable outcomes.")
        ]
    chunks = [missing[i:i+2] for i in range(0, len(missing), 2)]
    return [(f"Week {i+1}", "Learn and practice: " + ", ".join(chunk) + ". Finish with a small hands-on task.")
            for i, chunk in enumerate(chunks[:4])]


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root {--bg:#080a12;--panel:#111625;--line:rgba(157,171,204,.15);--text:#f4f6ff;--muted:#a0abc3;--violet:#a99aff;--cyan:#68e7f5;--green:#4bdfa1;--amber:#ffca72;--red:#ff7d98;}
.stApp {background:radial-gradient(ellipse at 12% 0%,rgba(105,80,255,.18),transparent 30%),radial-gradient(ellipse at 95% 15%,rgba(38,198,218,.10),transparent 28%),#080a12;color:var(--text);font-family:'DM Sans',sans-serif;}
.block-container {max-width:1480px;padding:1.6rem 2.4rem 4rem;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em;}
h1 {font-size:2.7rem!important;} h2 {font-size:1.7rem!important;}
p,label,.stCaption {color:var(--muted);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#111626,#0b0e18);border-right:1px solid var(--line);}
[data-testid="stSidebar"] h2 {font-size:1.15rem!important;}
[data-testid="stMetric"] {background:linear-gradient(145deg,#171e32,#101522);border:1px solid var(--line);border-radius:17px;padding:13px 15px;min-height:95px;}
[data-testid="stMetricLabel"] {color:#aab5cd!important;}
[data-testid="stMetricValue"] {font-family:'Space Grotesk',sans-serif;color:#f4f6ff!important;}
.stButton>button,.stDownloadButton>button {
  border:1px solid rgba(196,181,253,.85) !important;
  border-radius:12px;
  background:linear-gradient(105deg,#8067f5,#9b83ff) !important;
  color:#ffffff !important;
  font-weight:700 !important;
  min-height:2.85rem;
  box-shadow:0 5px 16px rgba(120,103,240,.16);
  transition:transform .18s,box-shadow .18s,background .18s;
}
.stButton>button p,.stButton>button span,.stDownloadButton>button p,.stDownloadButton>button span {
  color:#ffffff !important;
  font-weight:700 !important;
  opacity:1 !important;
}
.stButton>button:hover,.stDownloadButton>button:hover {
  transform:translateY(-1px);
  background:linear-gradient(105deg,#755bea,#8d72f5) !important;
  box-shadow:0 7px 20px rgba(120,103,240,.23);
  color:#ffffff !important;
  border-color:#ded8ff !important;
}
.stButton>button:disabled,.stDownloadButton>button:disabled {
  background:#38334f !important;
  color:#ded9f7 !important;
  border-color:#51496d !important;
  box-shadow:none !important;
  opacity:1 !important;
}
.stButton>button:disabled p,.stButton>button:disabled span {
  color:#ded9f7 !important;
  opacity:1 !important;
}
.stTextArea textarea,[data-baseweb="select"]>div {background:#101626!important;border:1px solid rgba(157,171,204,.2)!important;border-radius:12px!important;color:#f4f6ff!important;}
div[data-testid="stFileUploader"] section {background:linear-gradient(145deg,rgba(24,30,50,.8),rgba(13,18,31,.9));border:1px dashed rgba(169,154,255,.55);border-radius:18px;padding:1.5rem;transition:all .2s;}
div[data-testid="stFileUploader"] section:hover {border-color:var(--cyan);background:rgba(104,231,245,.05);}
.hero {position:relative;overflow:hidden;padding:38px 40px;border:1px solid rgba(169,154,255,.32);border-radius:28px;background:linear-gradient(112deg,rgba(27,29,59,.98),rgba(13,29,47,.98) 68%,rgba(10,43,50,.96));margin-bottom:22px;box-shadow:0 25px 70px rgba(0,0,0,.2);animation:enter .55s ease both;}
.hero:before {content:"";position:absolute;width:280px;height:280px;right:5%;top:-190px;border-radius:50%;background:rgba(104,231,245,.12);filter:blur(20px);animation:glow 7s ease-in-out infinite alternate;}
.hero:after {content:"";position:absolute;width:240px;height:240px;right:-55px;top:-100px;border:1px solid rgba(104,231,245,.28);border-radius:50%;box-shadow:0 0 0 24px rgba(104,231,245,.035),0 0 0 50px rgba(169,154,255,.04);}
.hero h1 {color:white!important;margin:.55rem 0 .4rem!important;position:relative;z-index:1;}
.hero p {max-width:740px;font-size:1.03rem;line-height:1.7;position:relative;z-index:1;}
.eyebrow {color:#c6bdff;font-size:.73rem;letter-spacing:.16em;font-weight:700;text-transform:uppercase;position:relative;z-index:1;}
.panel {background:linear-gradient(145deg,rgba(20,27,45,.96),rgba(12,17,30,.97));border:1px solid var(--line);border-radius:21px;padding:23px;margin-bottom:15px;box-shadow:0 12px 35px rgba(0,0,0,.1);transition:border-color .2s,transform .2s;}
.panel:hover {border-color:rgba(169,154,255,.4);transform:translateY(-1px);}
.panel-title {font-family:'Space Grotesk',sans-serif;font-size:1.08rem;font-weight:700;color:var(--text);margin-bottom:6px;}
.subtle {color:var(--muted);font-size:.88rem;line-height:1.6;}
.pill {display:inline-flex;padding:8px 12px;border-radius:999px;font-size:.83rem;font-weight:600;margin:4px 5px 4px 0;border:1px solid;transition:transform .18s;}
.pill:hover {transform:translateY(-2px);}
.pill-green {color:var(--green);background:rgba(75,223,161,.09);border-color:rgba(75,223,161,.27);}
.pill-amber {color:var(--amber);background:rgba(255,202,114,.09);border-color:rgba(255,202,114,.27);}
.pill-red {color:var(--red);background:rgba(255,125,152,.09);border-color:rgba(255,125,152,.27);}
.pill-neutral {color:#c3cce0;background:rgba(148,163,184,.08);border-color:var(--line);}
.section-heading {display:flex;align-items:center;justify-content:space-between;gap:12px;margin:22px 0 9px;}
.section-heading h3 {margin:0;font-size:1.12rem!important;}
.count {border-radius:999px;padding:5px 10px;font-size:.78rem;background:rgba(148,163,184,.1);color:var(--muted);}
.gauge-wrap {display:flex;align-items:center;justify-content:center;flex-direction:column;padding:10px 0;}
.gauge {width:230px;max-width:100%;filter:drop-shadow(0 0 18px rgba(169,154,255,.13));}
.gauge-track {stroke:rgba(148,163,184,.17);}
.gauge-value {stroke:url(#gaugeGrad);stroke-linecap:round;transform:rotate(-90deg);transform-origin:100px 100px;animation:gaugeIn 1.1s cubic-bezier(.2,.8,.2,1) both;}
.gauge-number {fill:#f5f6ff;font-family:'Space Grotesk',sans-serif;font-size:31px;font-weight:700;text-anchor:middle;}
.gauge-label {fill:#a0abc3;font-size:10px;letter-spacing:2px;text-anchor:middle;}
.skill-row {display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 15px;background:rgba(255,255,255,.025);border:1px solid var(--line);border-radius:13px;margin:8px 0;transition:all .2s;}
.skill-row:hover {transform:translateX(3px);background:rgba(169,154,255,.055);border-color:rgba(169,154,255,.3);}
.skill-name {color:var(--text);font-weight:600;}
.priority {font-size:.75rem;border-radius:999px;padding:5px 9px;white-space:nowrap;}
.result-intro {border:1px solid rgba(169,154,255,.22);border-radius:16px;padding:15px 18px;background:linear-gradient(100deg,rgba(169,154,255,.08),rgba(104,231,245,.04));margin:12px 0 18px;}
.mini-label {font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:#a0abc3;font-weight:700;}
.stTabs [data-baseweb="tab-list"] {gap:7px;overflow-x:auto;padding-bottom:6px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"] {border-radius:10px 10px 0 0;padding:12px 16px;white-space:nowrap;}
.stTabs [aria-selected="true"] {color:var(--violet)!important;border-bottom-color:var(--violet)!important;}
div[data-testid="stProgress"]>div>div {background:linear-gradient(90deg,#68e7f5,#a99aff)!important;border-radius:999px;}
div[data-testid="stProgress"]>div {background:rgba(148,163,184,.14);border-radius:999px;}
@keyframes enter {from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow {from{transform:translate(0,0)}to{transform:translate(-25px,25px)}}
@keyframes gaugeIn {from{stroke-dashoffset:283}}
@media(max-width:900px){.block-container{padding:1rem 1rem 3rem}.hero{padding:26px 22px}.hero h1{font-size:2.1rem!important}.panel{padding:17px}.gauge{width:185px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">✦ CAREER INTELLIGENCE PLATFORM &nbsp; / &nbsp; RESUME INSIGHTS</div>
  <h1>SkillBridge <span style="background:linear-gradient(90deg,#fff 10%,#b8adff 58%,#70e7f5 100%);-webkit-background-clip:text;background-clip:text;color:transparent">AI</span></h1>
  <p>Turn your resume into a focused action plan. See your role fit, identify skill gaps, and know exactly what to learn next.</p>
  <div style="display:flex;flex-wrap:wrap;gap:9px;margin-top:22px;position:relative;z-index:2">
    <span style="border:1px solid rgba(255,255,255,.13);background:rgba(255,255,255,.055);padding:7px 11px;border-radius:999px;color:#dce5ff;font-size:.78rem">◉ Role-specific matching</span>
    <span style="border:1px solid rgba(255,255,255,.13);background:rgba(255,255,255,.055);padding:7px 11px;border-radius:999px;color:#dce5ff;font-size:.78rem">↗ Actionable learning plan</span>
    <span style="border:1px solid rgba(255,255,255,.13);background:rgba(255,255,255,.055);padding:7px 11px;border-radius:999px;color:#dce5ff;font-size:.78rem">⌁ Resume skill signals</span>
  </div>
</div>
""", unsafe_allow_html=True)
st.caption("Prototype estimate based on extracted resume text and configured role requirements — not a hiring probability. Review evidence snippets and validate skills before relying on the score.")

with st.sidebar:
    st.markdown("## ⚙️ Analysis setup")
    st.caption("Personalize your skill-gap report")
    role = st.selectbox("Target job role", list(ROLE_SKILLS.keys()))
    custom_jd = st.text_area("Job description (optional)", height=160, placeholder="Paste the job description to include additional role-specific skills…")
    st.markdown("---")
    st.markdown("**How scoring works**")
    st.caption("Skills are detected from resume text using keyword and alias matching. A mention is not proof of proficiency.")
    st.markdown("---")
    st.caption("🔒 Demo privacy: files are processed in this app session. Avoid uploading sensitive personal data to public demos.")

st.markdown('<div class="eyebrow" style="margin:24px 0 8px">01 / START HERE</div><div class="panel"><div class="panel-title" style="font-size:1.25rem">Build your skill-match report</div><div class="subtle">Drop in your resume or paste the text below. We’ll compare it with your target role and turn gaps into a practical learning plan.</div></div>', unsafe_allow_html=True)
left, right = st.columns([1.15, .85], gap="large")
with left:
    uploaded = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    pasted_resume = st.text_area("Or paste resume text", height=180, placeholder="Paste resume text here…")
with right:
    st.markdown("""
    <div class="panel" style="height:100%">
      <div class="mini-label">YOUR REPORT</div>
      <div class="panel-title" style="margin-top:8px">What you'll get</div>
      <div class="subtle">✦ Overall role-match score<br><br>✦ Matched, partial and missing skills<br><br>✦ Prioritized skill gaps<br><br>✦ Curated learning resources<br><br>✦ A practical learning roadmap<br><br>✦ Downloadable text report</div>
    </div>
    """, unsafe_allow_html=True)

run = st.button("✦  Analyze my role fit", type="primary", use_container_width=True)

if run:
    resume_text = pasted_resume.strip()
    if uploaded:
        try:
            resume_text = extract_text(uploaded).strip()
        except Exception as e:
            st.error(str(e))
            st.stop()
    if not resume_text:
        st.warning("Upload a resume or paste resume text to begin.")
        st.stop()

    requirements = ROLE_SKILLS[role].copy()
    if custom_jd.strip():
        jd_skills = find_skills(custom_jd, list(RESOURCES.keys()) + list({s for r in ROLE_SKILLS.values() for s in r}))
        for s in jd_skills:
            requirements.setdefault(s, 0.7)

    detected = find_skills(resume_text, list(RESOURCES.keys()) + list({s for r in ROLE_SKILLS.values() for s in r}))
    matched = [s for s in requirements if s in detected]
    missing = [s for s in requirements if s not in detected]

    # Classify a skill as partial only when a qualifier is attached to that
    # individual mention. Split comma-separated skill lists as well as sentences
    # and lines so "PyTorch basics" does not downgrade unrelated skills nearby.
    qualifier_pattern = re.compile(
        r"\b(?:basic(?:s)?|beginner(?:-level)?|learning|learner|"
        r"familiar(?:ity)?(?: with)?|exposure to|currently learning|"
        r"currently studying|introductory|novice)\b",
        re.IGNORECASE,
    )

    def skill_has_local_qualifier(text, skill):
        aliases = ALIASES.get(skill.lower(), [skill.lower()])
        fragments = re.split(r"[,;|\n•]+|(?<=[.!?])\s+", text)
        for fragment in fragments:
            low = re.sub(r"\s+", " ", fragment.lower()).strip()
            for alias in aliases:
                alias_pattern = r"(?<![a-z0-9+#])" + re.escape(alias) + r"(?![a-z0-9+#])"
                for match in re.finditer(alias_pattern, low):
                    start_pos, end_pos = match.span()
                    window = low[max(0, start_pos - 28):min(len(low), end_pos + 28)]
                    if qualifier_pattern.search(window):
                        return True
        return False

    partial = []
    for skill in matched[:]:
        if skill_has_local_qualifier(resume_text, skill):
            partial.append(skill)
            matched.remove(skill)

    total_weight = sum(requirements.values()) or 1
    score = round(100 * (sum(requirements[s] for s in matched) + .5 * sum(requirements[s] for s in partial)) / total_weight)
    priority_missing = sorted(missing, key=lambda s: requirements[s], reverse=True)

    st.markdown("---")
    st.markdown(f'<div class="eyebrow">02 / ANALYSIS COMPLETE</div><h2 style="margin-top:8px">Your {role} readiness snapshot</h2><p class="subtle">What aligns today, what needs work, and where to focus next.</p>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .result-intro {border:1px solid rgba(165,151,255,.2);border-radius:18px;padding:15px 18px;background:linear-gradient(100deg,rgba(165,151,255,.07),rgba(112,231,245,.035));margin:12px 0 18px}
    .result-intro strong {color:#e9e5ff}
    .mini-label {font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:#9ba8c2;font-weight:700}
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="result-intro"><strong>What this means:</strong> Use the score as a resume-keyword alignment signal, then prioritize high-weight gaps and prove your strengths through projects.</div>', unsafe_allow_html=True)
    a, b = st.columns([.8, 1.2], gap="large")
    with a:
        circumference = 2 * 3.14159265 * 45
        offset = circumference * (1 - score / 100)
        st.markdown(f"""
        <div class="panel">
          <div class="panel-title">Overall skill match</div>
          <div class="gauge-wrap">
            <svg class="gauge" viewBox="0 0 200 200" role="img" aria-label="Estimated skill match {score} percent">
              <defs><linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#67e8f9"/><stop offset="100%" stop-color="#9b8cff"/></linearGradient></defs>
              <circle class="gauge-track" cx="100" cy="100" r="45" fill="none" stroke-width="11"/>
              <circle class="gauge-value" cx="100" cy="100" r="45" fill="none" stroke="url(#gaugeGrad)" stroke-width="11" stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"/>
              <text class="gauge-number" x="100" y="98">{score}%</text><text class="gauge-label" x="100" y="118">ROLE MATCH</text>
            </svg>
            <div class="subtle" style="text-align:center">Estimated alignment with role requirements</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel" style="padding:20px 22px 16px"><div class="panel-title">Your skill breakdown</div><div class="subtle">Keyword-based resume analysis</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3, gap="small")
        m1.metric("✓ Matched", len(matched))
        m2.metric("◐ Partial", len(partial))
        m3.metric("＋ Missing", len(missing))
        st.markdown(f'<div style="margin-top:14px;display:flex;align-items:center;justify-content:space-between;gap:12px"><span class="mini-label">WEIGHTED ROLE ALIGNMENT</span><strong style="color:#e8e4ff;font-size:1.05rem">{score}%</strong></div><div style="height:9px;background:rgba(148,163,184,.15);border-radius:99px;overflow:hidden;margin-top:8px"><div style="height:100%;width:{score}%;background:linear-gradient(90deg,#70e7f5,#a597ff);border-radius:99px;box-shadow:0 0 18px rgba(165,151,255,.22)"></div></div><div class="subtle" style="margin-top:12px">Role requirements scanned: <strong style="color:#edf2ff">{len(requirements)}</strong> &nbsp;·&nbsp; Recognized resume skills: <strong style="color:#edf2ff">{len(detected)}</strong></div></div>', unsafe_allow_html=True)

    # Dedicated sections keep each status visually distinct instead of mixing all skills together.
    def render_skill_section(title, skills, kind, description):
        colors = {"green": "#42d392", "amber": "#f6bd60", "red": "#ff718b"}
        symbols = {"green": "✓", "amber": "◐", "red": "＋"}
        st.markdown(f'<div class="section-heading"><h3 style="color:{colors[kind]}">{symbols[kind]} {title}</h3><span class="count">{len(skills)} skills</span></div><div class="subtle">{description}</div>', unsafe_allow_html=True)
        if not skills:
            st.markdown('<div class="panel"><span class="subtle">Nothing to show in this section for the current resume.</span></div>', unsafe_allow_html=True)
            return
        pills = "".join(f'<span class="pill pill-{"green" if kind=="green" else "amber" if kind=="amber" else "red"}">{skill}</span>' for skill in skills)
        st.markdown(f'<div class="panel">{pills}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["✦ Skill overview", "◎ Close the gaps", "↗ Learning resources", "☷ Roadmap & report"])
    with tab1:
        render_skill_section("Matched skills", matched, "green", "Skills found in the resume without an explicit beginner/learning qualifier.")
        render_skill_section("Partially matched", partial, "amber", "Skills mentioned with qualifiers such as basic, learning, or familiar with.")
        render_skill_section("Missing skills", missing, "red", "Role requirements not detected in the resume text. This does not prove you lack the skill.")
        st.markdown('<div class="panel"><div class="panel-title">Resume evidence</div><div class="subtle">Review snippets where matched skill keywords were detected. These support transparency but do not prove proficiency.</div></div>', unsafe_allow_html=True)
        for skill in (matched + partial)[:8]:
            with st.expander(f"{skill} · resume evidence"):
                snippets = evidence_for_skill(resume_text, skill)
                if snippets:
                    for snippet in snippets:
                        st.write(f"“{snippet}”")
                else:
                    st.caption("Skill keyword detected, but a concise evidence snippet could not be extracted.")
        if detected:
            st.write("**All recognized skills:** " + ", ".join(detected))
        else:
            st.info("No known skills detected. Try a text-based resume or check the extracted wording.")
    with tab2:
        st.markdown('<div class="panel"><div class="panel-title">Your next best moves</div><div class="subtle">Start with high-weight skills that are not yet visible in your resume.</div></div>', unsafe_allow_html=True)
        if priority_missing:
            for i, skill in enumerate(priority_missing, 1):
                priority = "High priority" if requirements[skill] >= .8 else "Medium priority"
                color = "#ff718b" if requirements[skill] >= .8 else "#f6bd60"
                st.markdown(f'<div class="skill-row"><div><div class="skill-name">{i:02d} &nbsp; {skill}</div><div class="subtle">Role weight: {requirements[skill]:.1f}</div></div><span class="priority" style="color:{color};background:rgba(255,255,255,.05)">{priority}</span></div>', unsafe_allow_html=True)
        else:
            st.success("No gaps found among the configured skills. Validate your proficiency with projects and interview practice.")
        st.warning("This prototype detects text mentions only. Validate your skills with practical work and human review.")
    with tab3:
        resources_for_missing = [s for s in priority_missing if s in RESOURCES]
        if resources_for_missing:
            for skill in resources_for_missing:
                label, url = RESOURCES[skill]
                st.markdown(f'<div class="skill-row"><div><div class="skill-name">{skill}</div><div class="subtle">{label}</div></div><a href="{url}" target="_blank" style="color:#a99cff;text-decoration:none;font-weight:700;white-space:nowrap">Open resource ↗</a></div>', unsafe_allow_html=True)
        else:
            st.info("No missing-skill resources to recommend. Review the roadmap and validate skills through projects.")
        st.caption("Curated external learning links. Check current availability and suitability before sharing.")
    with tab4:
        st.markdown('<div class="panel"><div class="panel-title">A practical learning roadmap</div><div class="subtle">Small, focused steps beat trying to learn everything at once.</div></div>', unsafe_allow_html=True)
        for week, task in get_roadmap(priority_missing):
            st.markdown(f'<div class="skill-row"><div><div class="skill-name">{week}</div><div class="subtle">{task}</div></div><span class="priority" style="color:#a99cff;background:rgba(155,140,255,.1)">PLAN</span></div>', unsafe_allow_html=True)
        project_map = {
            "Backend Developer": "Build a REST API with authentication, database persistence, validation, and automated tests.",
            "Frontend Developer": "Build a responsive React dashboard that consumes an API and includes loading/error states.",
            "Full-Stack Developer": "Build a full-stack task or expense tracker with authentication and CRUD operations.",
            "Data Analyst": "Analyze a public dataset using SQL and build a Power BI dashboard with written insights.",
            "Data Scientist": "Train and evaluate a baseline ML model; document data cleaning, metrics, and limitations.",
            "Machine Learning Engineer": "Serve a small ML model through an API with input validation and a reproducible setup.",
            "Software Engineer": "Build a tested application and document data structures, complexity, and design decisions."
        }
        st.markdown(f'<div class="panel"><div class="panel-title">Portfolio project to prove your skills</div><div class="subtle">{project_map.get(role, "Build and document a role-specific project.")}</div></div>', unsafe_allow_html=True)
        report = [
            "SKILLBRIDGE AI — RESUME ANALYSIS REPORT", f"Desired role: {role}", f"Estimated role match: {score}%",
            f"Matched skills: {', '.join(matched) if matched else 'None detected'}",
            f"Partially matched skills: {', '.join(partial) if partial else 'None detected'}",
            f"Potential gaps: {', '.join(missing) if missing else 'None detected'}", "", "LEARNING RESOURCES:"
        ]
        for skill in priority_missing:
            if skill in RESOURCES:
                label, url = RESOURCES[skill]
                report.append(f"- {skill}: {label} — {url}")
        report += ["", "SKILL BREAKDOWN:",
                   f"Matched: {', '.join(matched) if matched else 'None detected'}",
                   f"Partial: {', '.join(partial) if partial else 'None detected'}",
                   f"Missing: {', '.join(missing) if missing else 'None detected'}"]
        report += ["", "ROADMAP:"] + [f"{week}: {task}" for week, task in get_roadmap(priority_missing)]
        report += ["", "RECOMMENDED NEXT STEPS:",
                   "1. Validate matched skills with a project, code sample, or assessment.",
                   "2. Pick the two highest-priority gaps and practice them in a small project.",
                   "3. Update the resume with specific actions and measurable outcomes.",
                   "", "Disclaimer: This is a prototype estimate, not a hiring probability or validated competency assessment."]
        report_text = "\n".join(report)
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("↓  Download TXT report", report_text, file_name="skillbridge_report.txt", mime="text/plain", use_container_width=True)
        with d2:
            try:
                pdf_bytes = build_pdf_report(report, title=f"{role} — Skill Gap Report")
                st.download_button("↓  Download PDF report", pdf_bytes, file_name="skillbridge_report.pdf", mime="application/pdf", use_container_width=True)
            except ImportError:
                st.info("To enable PDF export, install reportlab with: python -m pip install reportlab")

st.markdown("---")
st.caption("SkillBridge AI · Prototype limitations: keyword/alias-based extraction, curated role templates, and heuristic scoring. Next upgrades: semantic matching, sentence-level evidence, assessment-based proficiency, and PDF report export.")
