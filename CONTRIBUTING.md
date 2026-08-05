# Contributing

## Setup
git clone https://github.com/suriyaethiraj/pm-user-research-engine.git
cd pm-user-research-engine
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

## Run
streamlit run interview_summarizer/app.py

## Before submitting a PR
- python evals.py passes (run from interview_summarizer/)
- CHANGELOG.md updated
- No secrets committed
- pip-audit clean
