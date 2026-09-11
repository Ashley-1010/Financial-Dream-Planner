import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.financial_tools import future_cost, monthly_investment, feasibility, goal_category
import pytest

def test_inflation_6_percent():
    assert round(future_cost(100000,1),2)==106000.00
def test_zero_timeline():
    with pytest.raises(ValueError): future_cost(100000,0)
def test_negative_timeline():
    with pytest.raises(ValueError): future_cost(100000,-1)
def test_monthly_positive():
    assert monthly_investment(100000,5)>0
def test_feasible_surplus():
    x=feasibility(10000,100000,20); assert x["surplus_or_shortfall"]==10000
def test_shortfall_visible():
    x=feasibility(30000,100000,20); assert x["surplus_or_shortfall"]==-10000
def test_saving_zero():
    x=feasibility(10000,100000,0); assert x["available_capacity"]==0
def test_saving_100():
    x=feasibility(10000,100000,100); assert x["available_capacity"]==100000
def test_saving_above_100():
    with pytest.raises(ValueError): feasibility(10000,100000,101)
def test_saving_below_0():
    with pytest.raises(ValueError): feasibility(10000,100000,-1)
def test_goal_categories():
    assert goal_category(3)=="Short-term"
    assert goal_category(7)=="Medium-term"
    assert goal_category(8)=="Long-term"