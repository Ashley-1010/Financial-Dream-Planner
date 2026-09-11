"""Train and compare the two approved salary regression models.

Models: Linear Regression and Decision Tree Regressor.
Experience is intentionally excluded because every target user is a fresher.
"""
from pathlib import Path  
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "salary_data.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)
TARGET = "Monthly_Salary"
FEATURES = ["Age", "City", "Education", "Job_Role"]  # Experience excluded as per requirements.

def main():
    df = pd.read_csv(DATA_PATH).dropna(subset=[TARGET]).copy()
    X, y = df[FEATURES], df[TARGET]

    numeric_features = ["Age"]
    categorical_features = ["City", "Education", "Job_Role"]
    preprocessor = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical_features),
    ])

    # ONLY these two models are used in the project.
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(max_depth=6, random_state=42),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    results, pipelines = [], {}
    for name, model in models.items():
        pipe = Pipeline([("preprocessor", preprocessor), ("model", model)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        results.append({
            "model": name,
            "MAE": round(float(mean_absolute_error(y_test, pred)), 2),
            "R2": round(float(r2_score(y_test, pred)), 4),
        })
        pipelines[name] = pipe

    # Selection rule: highest R2; if tied, lower MAE.
    results.sort(key=lambda x: (-x["R2"], x["MAE"]))
    best_name = results[0]["model"]
    joblib.dump(pipelines[best_name], MODEL_DIR / "salary_model.joblib")
    (MODEL_DIR / "model_comparison.json").write_text(json.dumps({
        "models_compared": ["Linear Regression", "Decision Tree Regressor"],
        "selection_rule": "Highest R2; ties broken by lowest MAE.",
        "best_model": best_name,
        "results": results,
    }, indent=2))

    print("\nModel comparison:")
    for r in results:
        print(f"{r['model']:<25} MAE={r['MAE']:<10} R2={r['R2']}")
    print(f"\nSelected model: {best_name}")

if __name__ == "__main__":
    main()