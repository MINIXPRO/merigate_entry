import frappe

# ─────────────────────────────────────────────
# Global Config
# ─────────────────────────────────────────────
ALLOWED_ROLES = ["Merigate Entry User"]


# ─────────────────────────────────────────────
# Helper: Role Check
# ─────────────────────────────────────────────
def has_merigate_access(user_email):
    roles = frappe.get_roles(user_email)
    return any(role in roles for role in ALLOWED_ROLES)


# ─────────────────────────────────────────────
# 1. Login
# ─────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def login_user(usr, pwd):
    try:
        if not usr or not pwd:
            frappe.response["message"] = {
                "status": "error",
                "message": "usr and pwd are required."
            }
            return

        if not frappe.db.exists("User", usr):
            frappe.response["message"] = {
                "status": "error",
                "message": "User not found. Contact admin."
            }
            return

        from frappe.auth import LoginManager
        try:
            lm = LoginManager()
            lm.authenticate(user=usr, pwd=pwd)
            lm.post_login()
            frappe.db.commit()
        except Exception:
            frappe.response["message"] = {
                "status": "error",
                "message": "Invalid credentials."
            }
            return

        if not has_merigate_access(usr):
            frappe.local.login_manager.logout()
            frappe.db.commit()
            frappe.response["message"] = {
                "status": "error",
                "message": "Access not assigned. Contact admin."
            }
            return

        frappe.response["message"] = {
            "status": "success",
            "message": "Login successful",
            "full_name": frappe.db.get_value("User", usr, "full_name"),
            "sid": frappe.session.sid
        }
        return

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "login_user Error")
        frappe.response["message"] = {
            "status": "error",
            "message": str(e)
        }
        return


# ─────────────────────────────────────────────
# 2. Create Merigate Entry
# ─────────────────────────────────────────────
@frappe.whitelist(allow_guest=False)
def create_merigate_entry(**kwargs):
    from frappe.utils.file_manager import save_file

    SKIP_FIELDS = {"name", "doctype", "owner", "creation", "modified", "cmd", "file", "docname"}

    if frappe.session.user == "Guest":
        frappe.response.http_status_code = 401
        frappe.response["message"] = {
            "status": "error",
            "code": 401,
            "message": "Session expired. Please login again to get a new SID."
        }
        return

    if not has_merigate_access(frappe.session.user):
        frappe.response["message"] = {
            "status": "error",
            "message": "Access denied. Contact admin."
        }
        return

    try:
        # ── Gate Entry No is mandatory and becomes the document ID ──
        gate_entry_no = kwargs.get('gate_entry_no')
        if not gate_entry_no:
            frappe.response["message"] = {
                "status": "error",
                "message": "gate_entry_no is required."
            }
            return

        # ── Handle duplicate gate_entry_no ──
        if frappe.db.exists("Merigate Entry", gate_entry_no):
            count = frappe.db.count("Merigate Entry", filters={"gate_entry_no": gate_entry_no})
            gate_entry_no = f"{gate_entry_no}-{count}"

        doc = frappe.new_doc("Merigate Entry")

        # ── Map form fields to document ──
        for key, value in kwargs.items():
            if key not in SKIP_FIELDS and hasattr(doc, key):
                setattr(doc, key, value)

        # ── Set default values ──
        if not doc.get("category"):
            doc.category = "General Purchase"

        if not doc.get("status"):
            doc.status = "Open"

        # ── Set document ID = gate_entry_no ──
        doc.name = gate_entry_no
        doc.docname = gate_entry_no

        # ── Handle duplicate on insert ──
        try:
            doc.insert(ignore_permissions=True)
        except frappe.DuplicateEntryError:
            doc.name = f"{gate_entry_no}-{frappe.generate_hash(length=4)}"
            doc.docname = doc.name
            doc.insert(ignore_permissions=True)

        # ── Handle optional file upload ──
        file_url = None
        if getattr(frappe.request, "files", None) and "file" in frappe.request.files:
            uploaded_file = frappe.request.files["file"]
            file_name = uploaded_file.filename

            if not file_name.endswith('.pdf'):
                frappe.response["message"] = {
                    "status": "error",
                    "message": "Only PDF files are allowed."
                }
                return

            file_content = uploaded_file.read()
            saved_file = save_file(
                fname=file_name,
                content=file_content,
                dt="Merigate Entry",
                dn=doc.name,
                folder="Home/Attachments",
                is_private=1
            )
            file_url = saved_file.file_url

        frappe.db.commit()

        frappe.response["message"] = {
            "status": "success",
            "docname": doc.name,
            "file_url": file_url if file_url else "No file uploaded"
        }
        return

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_merigate_entry Error")
        frappe.response["message"] = {
            "status": "error",
            "message": str(e)
        }
        return


# ─────────────────────────────────────────────
# 3. Logout
# ─────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def logout_user():
    try:
        if frappe.session.user == "Guest":
            frappe.response["message"] = {
                "status": "error",
                "code": 401,
                "message": "No active session. Please login first."
            }
            return

        user = frappe.session.user
        frappe.local.login_manager.logout()
        frappe.db.commit()

        frappe.response["message"] = {
            "status": "success",
            "message": "Logged out successfully.",
            "user": user
        }
        return

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "logout_user Error")
        frappe.response["message"] = {
            "status": "error",
            "message": "Logout failed. Session may already be expired."
        }
        return