import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

raw_cost = pd.read_csv(DATA_DIR / "raw_cost.csv")
cost_drivers = pd.read_csv(DATA_DIR / "cost_drivers.csv")

# Forecast assumptions
forecast_growth = {
    "API": 0.20,
    "Login": 0.10
}

# Expected cost baseline
expected_cost = {
    "API": 200,
    "Login": 80
}

# Merge raw cost with cost drivers
model = raw_cost.merge(cost_drivers, on="Workload", how="left")

# Forecast layer
model["Growth %"] = model["Workload"].map(forecast_growth)
model["Forecast Cost"] = model["Cost"] * (1 + model["Growth %"])

# Signal classification layer
model["Expected Cost"] = model["Workload"].map(expected_cost)
model["Variance"] = (model["Cost"] - model["Expected Cost"]) / model["Expected Cost"]

def classify_signal(row):
    if row["Variance"] >= 0.15:
        return "Inefficiency"
    elif row["Growth %"] > 0:
        return "Growth"
    else:
        return "Baseline"

model["Signal"] = model.apply(classify_signal, axis=1)

# Action layer
def recommend_action(row):
    if row["Signal"] == "Inefficiency":
        return "Investigate usage and reduce waste"
    elif row["Signal"] == "Growth":
        return "Update forecast and validate business demand"
    else:
        return "Monitor baseline"

model["Owner"] = model["Team"]
model["Action"] = model.apply(recommend_action, axis=1)
model["Status"] = "Open"

# Save outputs
OUTPUT_DIR.mkdir(exist_ok=True)

model.to_csv(OUTPUT_DIR / "finops_pipeline_output.csv", index=False)

print("FinOps pipeline completed.")
print(model[[
    "Workload",
    "Service",
    "Cost",
    "Expected Cost",
    "Forecast Cost",
    "Variance",
    "Signal",
    "Owner",
    "Action",
    "Status"
]])
# Priority scoring
model["Priority"] = model["Variance"].abs().apply(
    lambda x: "High" if x > 0.3 else "Medium" if x > 0.15 else "Low"
)

# Clean column order
final_columns = [
    "Date",
    "Service",
    "Workload",
    "Team",
    "Cost",
    "Expected Cost",
    "Forecast Cost",
    "Variance",
    "Signal",
    "Owner",
    "Action",
    "Status"
]

model = model[final_columns]

# Sort by highest variance
model = model.sort_values(by="Variance", ascending=False)
final_columns = [
    "Date",
    "Service",
    "Workload",
    "Team",
    "Cost",
    "Expected Cost",
    "Forecast Cost",
    "Variance",
    "Signal",
    "Priority",   # 👈 ADD THIS
    "Owner",
    "Action",
    "Status"
]