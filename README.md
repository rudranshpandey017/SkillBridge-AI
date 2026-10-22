# SkillBridge AI — Skill Gap Analyzer Prototype

A quick demo MVP: upload/paste a resume, select a desired job role, and generate a role-specific skill gap report with curated learning links and a roadmap.

## Run locally

1. Install Python 3.10+.
2. Unzip this folder and open a terminal inside it.
3. Create and activate a virtual environment (optional but recommended).
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Demo flow

- Use a text-based PDF/DOCX resume or paste resume text.
- Choose a target role from the sidebar.
- Optionally paste a job description.
- Click **Analyze resume against desired role**.
- Show the overview, gaps, resource links, roadmap, and downloadable report.

## Important limitations

This is a prototype, not a production hiring tool. The initial extractor uses skill keywords and aliases, and match scores are heuristic estimates. A missing keyword does not prove a missing skill; a mention does not prove proficiency. Do not present scores as hiring probabilities.

## Next upgrades

- Sentence Transformers semantic matching.
- Evidence snippets for each detected skill.
- Add more roles and editable role requirement templates.
- Evaluation against manually labeled resume/job-description pairs.
- PDF export, authentication, database persistence, and deployment.
