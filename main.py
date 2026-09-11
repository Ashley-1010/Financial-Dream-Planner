from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from tools.salary_tools import predict_salary
from tools.financial_tools import calculate_goal, feasibility, recommendation, get_current_goal_costs
from agent.agent import run_agent
from rag.rag_engine import answer_from_rag, build_store

BASE_DIR=Path(__file__).resolve().parent
app=FastAPI(title="Financial_Dream_Planner_AI", version="1.0.0",
            description="Local educational AI-powered financial goal planner to make financial dreams a reality.")

class SalaryRequest(BaseModel):
    age:int=Field(..., ge=18, le=70)
    city:str
    education:str
    job_role:str

class GoalRequest(BaseModel):
    city:str
    goal:str
    years:int=Field(..., gt=0, le=60)
    area_type:Optional[str]=None

class PlanGoal(BaseModel):
    goal:str
    years:int=Field(..., gt=0, le=60)

class PlanRequest(BaseModel):
    age:int=Field(..., ge=18, le=70)
    city:str
    education:str
    job_role:str
    saving_percentage:float=Field(..., ge=0, le=100)
    goals:List[PlanGoal]

class AgentRequest(BaseModel):
    message:str=Field(..., min_length=3)

class RagRequest(BaseModel):
    question:str=Field(..., min_length=3)

app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

@app.on_event("startup")
def startup():
    build_store()

@app.get("/")
def home():
    return FileResponse(BASE_DIR/"static/index.html")

@app.get("/api/health")
def health():
    return {"status":"ok","project":"Financial_Dream_Planner_AI","inflation_rate":0.06}

@app.post("/api/predict-salary")
def salary(req:SalaryRequest):
    try:
        predicted_salary=predict_salary(req.age,req.city,req.education,req.job_role,)
        return {"predicted_monthly_salary":round(predicted_salary,2)}
    except ValueError as e: raise HTTPException(400,str(e))
    except Exception as e: raise HTTPException(500,detail=f"Salary prediction failed: {str(e)}")

@app.post("/api/goal")
def goal(req:GoalRequest):
    try: return calculate_goal(req.city,req.goal,req.years,req.area_type)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Goal calculation failed: {str(e)}",
        )


@app.post("/api/plan")
def plan(req:PlanRequest):
    try:
        salary_value=predict_salary(req.age,req.city,req.education,req.job_role)
        goals=[calculate_goal(req.city,g.goal,g.years) for g in req.goals]
        total=sum(x["monthly_investment"] for x in goals)
        return {"salary_prediction":round(salary_value,2),"goals":goals,
                "total_monthly_required":round(total,2),
                "feasibility":feasibility(total,salary_value,req.saving_percentage)}
    #except Exception as e: raise HTTPException(400,str(e))
    except ValueError as e: raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/agent")
def agent(req:AgentRequest):
    try: return run_agent(req.message)
    except Exception as e: raise HTTPException(400,str(e))

@app.post("/api/rag")
def rag(req:RagRequest):
    return answer_from_rag(req.question)

@app.get("/api/cities")
def cities():
    import pandas as pd
    df=pd.read_csv(BASE_DIR/"data/city_goal_costs.csv")
    return {"cities":sorted(df.City.unique().tolist()),"area_types":sorted(df.Area_Type.unique().tolist())}

@app.get("/api/model-info")
def model_info():
    import json
    return json.loads((BASE_DIR/"models/model_comparison.json").read_text())
