
"""Local lightweight agent/router.
It identifies intent and delegates numeric work to deterministic tools.
No LLM is allowed to perform financial calculations.
"""
import re
from tools.salary_tools import predict_salary
from tools.financial_tools import (
    calculate_goal, feasibility, recommendation, get_current_goal_costs
)
from rag.rag_engine import answer_from_rag

GOALS = {"marriage": "Marriage", "car": "Car", "home": "Home"}

def _find_int(text, patterns, default=None):
    for p in patterns:
        m=re.search(p,text,re.I)
        if m: return int(m.group(1))
    return default

def parse_request(text):
    lower=text.lower()
    data={}
    age=_find_int(text,[r"\b(?:age\s*)?(\d{2})\s*(?:years?\s*old|,|\b)"])
    if age and 18 <= age <= 70: data["age"]=age
    cities=["Bangalore","Mumbai","Delhi","Hyderabad","Chennai","Pune","Kolkata","Ahmedabad","Jaipur","Lucknow"]
    educations=["MBA","B.E.","MCA","BCA","M.Sc","B.Tech","B.Sc","M.Tech"]
    roles=["Web Developer","Technical Support Engineer","Project Coordinator","Software Engineer","UI UX Designer","QA Engineer","Business Analyst","DevOps Engineer","Data Analyst","Data Scientist"]
    for c in cities:
        if c.lower() in lower: data["city"]=c; break
    for e in educations:
        if e.lower() in lower: data["education"]=e; break
    for r in roles:
        if r.lower() in lower: data["job_role"]=r; break
    m=re.search(r"save\s+(\d+(?:\.\d+)?)\s*%", text, re.I)
    if not m: m=re.search(r"saving(?:s)?\s*(?:target|percentage)?\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*%",text,re.I)
    if m: data["saving_percentage"]=float(m.group(1))
    for key,goal in GOALS.items():
        patterns=[rf"{key}.{{0,50}}?(?:after|in)\s+(\d+)\s+years?", rf"(\d+)\s+years?.{{0,30}}?{key}"]
        years=_find_int(text,patterns)
        if years is not None: data.setdefault("goals",[]).append({"goal":goal,"years":years})
    return data

def run_agent(text):
    lower=text.lower()
    # Basic prompt-injection protection: the user cannot override tool/system rules.
    injection_markers = [
        "ignore previous instructions", "ignore system instructions",
        "reveal system prompt", "bypass tools", "do not use tools"
    ]
    if any(marker in lower for marker in injection_markers):
        return {"intent":"blocked",
                "message":"Request blocked: system instructions and deterministic financial tools cannot be bypassed."}
    if any(k in lower for k in ["what is", "why ", "explain", "rag", "inflation", "investment category"]):
        return {"intent":"knowledge", **answer_from_rag(text)}

    data=parse_request(text)
    if "goals" not in data:
        return {"intent":"unknown",
                "message":"Please provide age, city, education, job role, saving percentage and goal timelines, or ask an approved knowledge-base question."}

    # Tool calls, kept separate from agent reasoning.
    salary=predict_salary(data.get("age",22), data.get("city","Bangalore"),
                          data.get("education","B.Tech"), data.get("job_role","Software Engineer"))
    goal_results=[]
    for g in data["goals"]:
        goal_results.append(calculate_goal(data.get("city","Bangalore"),g["goal"],g["years"]))
    total=sum(g["monthly_investment"] for g in goal_results)
    f=feasibility(total,salary,data.get("saving_percentage",20))
    return {"intent":"financial_plan","salary_prediction":round(salary,2),
            "goals":goal_results,"total_monthly_required":round(total,2),
            "feasibility":f,
            "agent_note":"Numeric values were produced by deterministic tools."}