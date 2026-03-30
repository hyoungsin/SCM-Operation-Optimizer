# SCM-MILP-PoC

## Project Goal
This project is a PoC for SCM MILP optimization.

Tech stack:
- Backend: Python, FastAPI, Pyomo, HiGHS, MongoDB
- Frontend: React (Vite)
- Frontend deployment: Vercel
- Backend deployment: separate Python server

## Fixed Rules
- Input is an Excel file with multiple sheets.
- Optimization flow:
  parse -> validate -> normalize -> build model -> solve -> output writer
- UI flow:
  Upload -> Validation -> Solve -> Download
- If duplicate rows exist, aggregate them.
- If a value is negative or null, convert it to 0.
- If correction happens, record it as warning with handling detail.
- If validation has error, solve must be blocked.

## PoC Scope
Build the initial working project skeleton for:
1. backend folder structure
2. frontend folder structure
3. upload API
4. validation API
5. solve API
6. download API
7. basic MongoDB run status management
8. initial UI pages for Upload / Validation / Solve / Download

## Important
This is a PoC.
Focus on clean structure and runnable skeleton first.
Do not over-engineer.
Use clear file separation and practical naming.

# SCM-MILP-PoC

Initial project skeleton for an SCM MILP PoC.

## Structure

- `docs/`: project guide and step documents
- `backend/`: FastAPI backend skeleton
- `frontend/`: React + Vite frontend skeleton
- `data/`: local upload/output/report storage

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend default URL: `http://127.0.0.1:8000`

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://127.0.0.1:5173`

## Notes

- This skeleton keeps business logic minimal on purpose.
- Upload, validation, solve, and download flows are placeholders.
- Optimization modules for parse, validate, normalize, model build, solve, and output write are created as extension points.
