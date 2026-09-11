from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "salary_model.joblib"
model = joblib.load(MODEL_PATH)

def predict_salary(age: int, city: str, education: str, job_role: str) -> float:
    print("here")
    if not isinstance(age, int) or age < 18 or age > 70:
        raise ValueError("Age must be between 18 and 70.")

    X = pd.DataFrame([{
        "Age": age, 
        "City": city,
        "Education": education,
        "Job_Role": job_role
    }])

    prediction = model.predict(X)[0]

    return float(prediction)

    #return float(model.predict(X)[0])

