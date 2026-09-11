"""Deterministic financial tools. The Agent calls these tools; it does not calculate numbers itself."""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
CITY_DATA = BASE_DIR / "data" / "city_goal_costs.csv"

#the project requirement explicitly asks for 6% per year. Therefore the application uses 6% = 0.06 as a decimal.
INFLATION_RATE = 0.06

EXPECTED_ANNUAL_RETURN = {
    "short": 0.06,
    "medium": 0.08,
    "long": 0.10,
}

#checks if timeline is valid or not. Timeline should not be negative and should be an integer to begin with
def validate_timeline(years: int):
    if not isinstance(years, int) or years <= 0 or years > 60:
        raise ValueError("Timeline must be a positive whole number of years or within a possible range.")

#calculating the future cost if inflation rate is 6% per year
def future_cost(current_cost: float, years: int) -> float:
    validate_timeline(years)
    # Explicit inflation calculation:
    # Future Cost = Current Cost × ((1 + 6%)^Years)
    return float(current_cost * ((1 + INFLATION_RATE) ** years))

#
def get_current_goal_costs(city: str, area_type: str | None = None) -> dict:
    df = pd.read_csv(CITY_DATA)
    city_matches = df[df["City"].str.lower() == city.strip().lower()]
    if city_matches.empty:
        raise ValueError(f"Unknown city: {city}")

    if area_type:
        area_matches = city_matches[
            city_matches["Area_Type"].str.lower() == area_type.strip().lower()
        ]
        if area_matches.empty:
            raise ValueError(f"Unknown area type '{area_type}' for {city}")
        row = area_matches.iloc[0]
        return {
            "Marriage": float(row["Marriage_Cost_Current"]),
            "Car": float(row["Car_Cost_Current"]),
            "Home": float(row["Home_Cost_Current"]),
        }

    # If no area is supplied, use the average of the available areas for that city.
    return {
        "Marriage": float(city_matches["Marriage_Cost_Current"].mean()),
        "Car": float(city_matches["Car_Cost_Current"].mean()),
        "Home": float(city_matches["Home_Cost_Current"].mean()),
    }

def goal_category(years: int) -> str:
    validate_timeline(years)
    if years <= 3:
        return "Short-term"
    if years >= 4 and years <= 7:
        return "Medium-term"
    return "Long-term"

def expected_return_for_goal(years: int) -> float:
    category = goal_category(years)
    return EXPECTED_ANNUAL_RETURN[{
        "Short-term": "short",
        "Medium-term": "medium",
        "Long-term": "long",
    }[category]]


def monthly_investment(future_amount: float, years: int, annual_return: float | None = None) -> float:
    validate_timeline(years)
    annual_return = annual_return if annual_return is not None else expected_return_for_goal(years)
    months = years * 12
    monthly_rate = annual_return / 12

    # Future Value of ordinary monthly contributions:
    # PMT = FV * r / ((1+r)^n - 1)
    if monthly_rate == 0:
        return future_amount / months
    return float(future_amount * monthly_rate / (((1 + monthly_rate) ** months) - 1))

def calculate_goal(city: str, goal: str, years: int, area_type: str | None = None) -> dict:
    costs = get_current_goal_costs(city, area_type)
    if goal not in costs:
        raise ValueError("Goal must be Marriage, Car, or Home.")
    current = costs[goal]
    future = future_cost(current, years)
    monthly = monthly_investment(future, years)
    return {
        "goal": goal,
        "timeline_years": years,
        "current_cost": round(current, 2),
        "future_cost": round(future, 2),
        "monthly_investment": round(monthly, 2),
        "category": goal_category(years),
        "assumed_annual_return": expected_return_for_goal(years),
    }

def feasibility(total_monthly_required: float, monthly_salary: float, saving_percentage: float) -> dict:
    if not 0 <= saving_percentage <= 100:
        raise ValueError("Saving percentage must be between 0 and 100.")
    capacity = monthly_salary * (saving_percentage / 100)
    gap = capacity - total_monthly_required
    if gap >= 0:
        status = "Achievable" if gap >= total_monthly_required * 0.10 else "Challenging"
    else:
        status = "Highly Challenging" if abs(gap) >= capacity * 0.50 else "Challenging"
    return {
        "monthly_salary": round(monthly_salary, 2),
        "saving_percentage": saving_percentage,
        "available_capacity": round(capacity, 2),
        "required_investment": round(total_monthly_required, 2),
        "surplus_or_shortfall": round(gap, 2),
        "status": status,
    }

def recommendation(years: int) -> dict:
    category = goal_category(years)
    rules = {
        "Short-term": "Lower-volatility / capital-preservation-oriented category",
        "Medium-term": "Diversified balanced category",
        "Long-term": "Diversified long-term growth-oriented category",
    }
    return {"time_horizon": category, "recommended_category": rules[category],
            "note": "Educational category only; no individual securities or guaranteed returns."}
