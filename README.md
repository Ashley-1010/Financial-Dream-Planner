# Financial_Dream_Planner_AI

A local end-to-end AI-powered financial dream and goal planner for final-year/fresher students.

## What this project does
1. Predicts a fresher's monthly salary using ML.
2. Compares Linear Regression and Decision Tree Regressor.
3. Estimates Marriage, Car and Home costs from the supplied city/goal dataset.
4. Applies **6% annual inflation**.
5. Calculates monthly investment requirements using deterministic Python formulas.
6. Performs feasibility analysis and shows a surplus/shortfall.
7. Recommends broad educational investment categories by time horizon.
8. Provides a lightweight local Agent that routes requests to tools.
9. Uses a local RAG knowledge base.
10. Exposes everything through FastAPI with a simple web UI.

## Important inflation requirement
The source assignment PDF says 0.06%, but the implementation requirement for this project explicitly changes that to **6% per year**. The code therefore contains:

`INFLATION_RATE = 0.06`

and:

`future_cost = current_cost * ((1 + INFLATION_RATE) ** years)`

This means ₹1,00,000 after 1 year becomes ₹1,06,000.

## Project structure
```text
Financial_Dream_Planner_AI/
├── agent/
│   └── agent.py
├── data/
│   ├── city_goal_costs.csv
│   └── salary_data.csv
├── knowledge_base/
│   ├── financial_guidelines.txt
│   ├── investment_categories.txt
│   └── goal_planning_rules.txt
├── models/
│   └── salary_model.joblib
├── rag/
│   ├── rag_engine.py
│   └── build_rag.py
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   ├── test_api.py
│   ├── test_financial_tools.py
│   └── test_cases.md
├── tools/
│   ├── financial_tools.py
│   └── salary_tool.py
├── main.py
├── train.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup in VS Code / Windows
```powershell
py -3.12 -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\activate
```

## Train the ML model
Run from the project root:
```powershell
python train.py
```
This creates:
- `models/salary_model.joblib`
- `models/model_comparison.json`

## Build/update RAG store
```powershell
python rag/build_rag.py
```
The application also builds the store automatically at startup.

## Run the web application
```powershell
uvicorn main:app --reload
```
Open:
`http://127.0.0.1:8000`

## Run tests
```powershell
pytest -q
```

## ML design
Features:
- Age
- City
- Education
- Job_Role

Target:
- Monthly_Salary

Experience is deliberately excluded because all users are treated as freshers.

Categorical columns are encoded with OneHotEncoder. Unknown categories are tolerated by the preprocessing pipeline so the application remains robust; the test suite also covers unknown inputs.

## Model selection
The training script evaluates:
- MAE (lower is better)
- R² (higher is better)

Selection rule:
**highest R²; ties are broken by lowest MAE.**

## Financial formulas
### Future cost
`Future Cost = Current Cost × (1 + 0.06)^Years`

### Monthly investment
For monthly compounding of the assumed return:
`PMT = FV × r / ((1+r)^n - 1)`

Where:
- FV = future goal amount
- r = annual expected return / 12
- n = years × 12

Educational assumptions:
- Short-term (1–3 years): 6%
- Medium-term (4–7 years): 8%
- Long-term (8+ years): 10%

## Feasibility
`Available capacity = predicted monthly salary × saving percentage`

`Surplus/shortfall = available capacity - total monthly requirement`

The application never hides a shortfall.

## Agent
The Agent identifies whether the request is:
- a financial planning request, or
- a knowledge/RAG question.

For a plan, it calls:
1. Salary Prediction Tool
2. Future Cost Tool
3. Investment Calculator Tool
4. Feasibility Tool

The Agent does not perform deterministic financial arithmetic itself.

## RAG
The local knowledge base has three documents. The RAG engine chunks them and stores local vector representations. It uses Sentence Transformers when available and a TF-IDF fallback if the embedding model is unavailable. If the similarity threshold is not met, it returns:
`Information unavailable in the local knowledge base.`

## Safety
This is an educational simulation, not professional financial advice. It does not recommend individual stocks and does not guarantee investment returns.

## GitHub checklist
Before pushing:
```powershell
git init
git add .
git commit -m "Initial Financial Dream Planner AI project"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Do not commit:
- `venv/`
- `__pycache__/`
- `.pytest_cache/`
- local secrets
- large downloaded model caches
