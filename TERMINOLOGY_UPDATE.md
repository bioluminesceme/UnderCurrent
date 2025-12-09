# Terminology Update: Readiness Score → Energy Budget

## Rationale
"Energy Budget" better resonates with ME/CFS patients and the concept of pacing/energy management.

## Files to Update

### Backend (Python)
- [ ] `backend/models.py`: Rename `ReadinessScore` table to `EnergyBudget`
- [ ] `backend/readiness_calculator.py`: Rename to `energy_budget_calculator.py`
- [ ] `backend/api/readiness.py`: Rename to `energy_budget.py`
- [ ] `backend/main.py`: Update router imports and paths

### Android (Kotlin)
- [ ] `HrvData.kt`: Rename `ReadinessScoreResponse` to `EnergyBudgetResponse`
- [ ] `CfsHrvApiClient.kt`: Update all readiness → energy_budget endpoints
- [ ] `HrvRepository.kt`: Update method names
- [ ] `HomeScreen.kt`: Update UI labels

### API Endpoints
- `/api/readiness/` → `/api/energy-budget/`

## Quick Rename Commands

```bash
# Backend
mv backend/readiness_calculator.py backend/energy_budget_calculator.py
mv backend/api/readiness.py backend/api/energy_budget.py

# Then find/replace:
# - ReadinessScore → EnergyBudget
# - readiness_score → energy_budget
# - Readiness → Energy Budget (in UI strings)
```

Would you like me to proceed with these updates?
