# Scam Checker

A simple web app to check and report scam phone numbers.

**Live demo:** https://scam-checker-ovcb.onrender.com

## Features

- Search a phone number to see verified scam reports
- "Under review" warning for numbers with unverified reports
- Report a scam number with a scam type, details, and email
- Delete your own report using the ID and delete code
- Admin login to verify or delete reports
- English and Malay interface

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Frontend:** HTML, CSS, JavaScript
- **Hosting:** Render

## Run Locally

1. Go to the backend folder: `cd backend`
2. Install the requirements: `pip install -r requirements.txt`
3. Create a `.env` file inside the backend folder with these lines:
   - `SUPABASE_URL=your_supabase_url`
   - `SUPABASE_SERVICE_ROLE_KEY=your_service_role_key`
   - `ADMIN_PASSWORD=your_admin_password`
4. Start the server: `python -m uvicorn api:app --reload --host 0.0.0.0`
5. Open http://localhost:8000 in your browser.
## API Docs

FastAPI generates interactive docs automatically at `/docs` (Swagger UI).

## Note

This is a bootcamp project. All data used is dummy data.
