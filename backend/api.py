# ============ IMPORTS ============
import os
import secrets
from datetime import date

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from supabase import create_client

# ============ SETTINGS & SUPABASE CONNECTION ============
load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)
TABLE = "reports"

# Public users only see these columns (delete code and email are NOT included)
PUBLIC_COLUMNS = "id, phone, scam_type, story, report_date, status"
# Admin also sees email to verify the report owner (delete code stays hidden)
ADMIN_COLUMNS = PUBLIC_COLUMNS + ", contact_email"

app = FastAPI()


# ============ REPORT DATA MODEL ============
class ReportIn(BaseModel):
    phone: str
    scam_type: str
    story: str
    contact_email: str


# ============ ADMIN SECURITY ============
def check_admin(x_admin_password: str | None = Header(default=None)):
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_password or x_admin_password != admin_password:
        raise HTTPException(status_code=401, detail="Kata laluan admin salah")


# ============ WEB PAGES ============
@app.get("/")
def homepage():
    return FileResponse("index.html")


@app.get("/laporan")
def laporan_page():
    return FileResponse("laporan.html")


@app.get("/admin")
def admin_page():
    return FileResponse("admin.html")


# ============ SEARCH (PUBLIC) ============
@app.get("/reports/search")
def search_reports(phone: str):
    rows = (
        supabase.table(TABLE)
        .select(PUBLIC_COLUMNS)
        .eq("phone", phone.strip())
        .eq("status", "Verified")
        .execute()
        .data
    )
    return rows


@app.get("/reports/pending-count")
def pending_count(phone: str):
    # Only the count, no report details or email
    rows = (
        supabase.table(TABLE)
        .select("id")
        .eq("phone", phone.strip())
        .eq("status", "New")
        .execute()
        .data
    )
    return {"pending": len(rows)}


# ============ CREATE REPORT ============
@app.post("/reports")
def create_report(report: ReportIn):
    email = report.contact_email.strip()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Email tidak sah")

    kod_padam = secrets.token_hex(3).upper()
    data = {
        "phone": report.phone.strip(),
        "scam_type": report.scam_type.strip(),
        "story": report.story.strip(),
        "contact_email": email,
        "report_date": date.today().isoformat(),
        "status": "New",
        "delete_code": kod_padam,
    }
    result = supabase.table(TABLE).insert(data).execute()
    return {"id": result.data[0]["id"], "kod_padam": kod_padam}


# ============ ADMIN: LIST REPORTS ============
@app.get("/admin/reports", dependencies=[Depends(check_admin)])
def admin_list_reports():
    rows = supabase.table(TABLE).select(ADMIN_COLUMNS).order("id").execute().data
    return rows


# ============ ADMIN: VERIFY REPORT ============
@app.patch("/reports/{report_id}/verify", dependencies=[Depends(check_admin)])
def verify_report(report_id: int):
    result = (
        supabase.table(TABLE)
        .update({"status": "Verified"})
        .eq("id", report_id)
        .execute()
    )
    return result.data


# ============ ADMIN: DELETE REPORT ============
@app.delete("/admin/reports/{report_id}", dependencies=[Depends(check_admin)])
def admin_delete_report(report_id: int):
    result = supabase.table(TABLE).delete().eq("id", report_id).execute()
    return result.data


# ============ DELETE BY USER ============
@app.delete("/reports/{report_id}")
def delete_report(report_id: int, kod_padam: str):
    result = (
        supabase.table(TABLE)
        .delete()
        .eq("id", report_id)
        .eq("delete_code", kod_padam)
        .execute()
    )
    return result.data