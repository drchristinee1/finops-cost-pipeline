# Data Model

## Raw Cost Input

| Field | Description |
|------|------------|
| Date | Usage date |
| Service | AWS service |
| Usage | Consumption metric |
| Cost | Actual cost |
| Team | Owning team |
| Workload | Logical system |

## Cost Drivers

| Field | Description |
|------|------------|
| Workload | System |
| Driver | Cost driver (requests, invocations) |
| Metric | Unit scale |
| Cost per Unit | Unit economics |

## Derived Fields

- Forecast Cost
- Expected Cost
- Variance
- Signal (Baseline / Growth / Inefficiency)
- Owner
- Action
- Status

## Key Concept

Cost is translated into:
- Unit economics
- Signals
- Actions

This enables engineering teams to act on cost insights.