import os
from datetime import date

from dotenv import load_dotenv
from supabase import create_client

# ===== SAMBUNG KE SUPABASE =====
load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)
TABLE = "reports"


def print_report(report):
    status = report.get("status") or "New"
    print(f"ID {report['id']} | {report['phone']} | {report['scam_type']} | {status}")


# ===== HELPER: MINTA NOMBOR =====
def ask_id(message):
    while True:
        text = input(message)
        try:
            return int(text)
        except ValueError:
            print("Please enter a number only.")


# ===== READ: SENARAI SEMUA =====
def list_reports():
    rows = supabase.table(TABLE).select("*").order("id").execute().data
    if not rows:
        print("No reports yet.")
        return
    for report in rows:
        print_report(report)


# ===== READ: CARI BY PHONE =====
def search_reports():
    search_phone = input("Enter phone number: ")
    rows = (
        supabase.table(TABLE)
        .select("*")
        .eq("phone", search_phone)
        .execute()
        .data
    )
    if not rows:
        print("No reports yet. This does not mean the number is safe.")
        return
    for report in rows:
        print_report(report)


# ===== CREATE =====
def create_report():
    print("--- New report ---")
    new_phone = input("Phone number: ")
    new_scam_type = input("Scam type: ")
    new_story = input("Story: ")

    supabase.table(TABLE).insert({
        "phone": new_phone,
        "scam_type": new_scam_type,
        "story": new_story,
        "report_date": date.today().isoformat(),
        "status": "New",
    }).execute()

    print("Report saved to Supabase.")
    list_reports()


# ===== UPDATE: VERIFY =====
def verify_report():
    print("--- Verify report ---")
    update_id = ask_id("Report ID to verify: ")

    result = (
        supabase.table(TABLE)
        .update({"status": "Verified"})
        .eq("id", update_id)
        .execute()
    )

    if result.data:
        print(f"Report {update_id} is now Verified.")
    else:
        print(f"Report {update_id} not found.")
    list_reports()


# ===== DELETE =====
def delete_report():
    print("--- Delete report ---")
    delete_id = ask_id("Report ID to delete: ")

    result = supabase.table(TABLE).delete().eq("id", delete_id).execute()

    if result.data:
        print(f"Report {delete_id} has been deleted.")
    else:
        print(f"Report {delete_id} not found.")
    list_reports()


# ===== MENU =====
while True:
    print("\n===== SCAM CHECKER =====")
    print("1. List all reports")
    print("2. Search by phone")
    print("3. Create report")
    print("4. Verify report")
    print("5. Delete report")
    print("0. Exit")

    choice = input("Choose: ")

    try:
        if choice == "1":
            list_reports()
        elif choice == "2":
            search_reports()
        elif choice == "3":
            create_report()
        elif choice == "4":
            verify_report()
        elif choice == "5":
            delete_report()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please choose 0 to 5.")
    except Exception as e:
        print("Error:", e)