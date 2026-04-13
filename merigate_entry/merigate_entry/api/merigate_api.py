import frappe


# ─────────────────────────────────────────────
# Global Config
# ─────────────────────────────────────────────
ERP_BASE_URL = "https://staging.microcrispr.com"


# ─────────────────────────────────────────────
# 1. Create / Update Merigate Entry
# ─────────────────────────────────────────────
@frappe.whitelist()
def create_merigate_entry(**kwargs):
    skip_fields = {"name", "doctype", "owner", "creation", "modified"}
    try:
        # Get docname
        docname = kwargs.get("name") or kwargs.get("docname")
        if not docname:
            frappe.throw("Merigate Doc Name is required")

        # Role check (SECURITY FIX)
        user_roles = frappe.get_roles(frappe.session.user)
        if not any(role in user_roles for role in ["Merigate Entry User", "System Manager"]):
            return {
                "status": "error",
                "message": "Access denied. Contact admin."
            }

        # Check if exists
        if frappe.db.exists("Merigate Entry", {"docname": docname}):
            doc = frappe.get_doc("Merigate Entry", {"docname": docname})
        else:
            doc = frappe.new_doc("Merigate Entry")
            doc.docname = docname   # Correct primary key usage

        # Map fields dynamically (OPTIMIZED)
        for key, value in kwargs.items():
            if key not in skip_fields and hasattr(doc, key):
                setattr(doc, key, value)

        # Defaults (if not passed)
        if not doc.category:
            doc.category = "General Purchase"

        if not doc.status:
            doc.status = "Open"

        # Save
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "docname": doc.docname,
            "message": "Merigate Entry saved successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_merigate_entry Error")
        return {
            "status": "error",
            "message": str(e)
        }


# ─────────────────────────────────────────────
# 2. Unified Login (Single Entry Point)
# ─────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def login_user(email, password, first_name="", last_name=""):
    try:
        # ── New user? ──
        if not frappe.db.exists("User", email):
            if not first_name:
                return {
                    "status": "error",
                    "message": "User not found. Provide first_name to create a new account."
                }

            user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "enabled": 1,
                "new_password": password,
                "send_welcome_email": 0,
            })
            user.insert(ignore_permissions=True)
            frappe.db.commit()

            return {
                "status": "success",
                "message": f"User '{email}' created successfully. Contact admin to assign access role."
            }

        # ── Existing user → authenticate ──
        try:
            frappe.local.login_manager.authenticate(email, password)
        except Exception:
            return {
                "status": "error",
                "message": "Invalid credentials"
            }

        # ── Role check ──
        roles = frappe.get_roles(email)
        if not any(role in roles for role in ["Merigate Entry User", "System Manager"]):
            return {
                "status": "error",
                "message": "Access not assigned. Contact admin."
            }

        # ── Generate token ──
        user = frappe.get_doc("User", email)
        api_key = frappe.generate_hash(length=15)
        api_secret = frappe.generate_hash(length=15)
        user.api_key = api_key
        user.api_secret = api_secret
        user.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "token": f"{api_key}:{api_secret}",
            "base_url": ERP_BASE_URL,
            "endpoint": f"{ERP_BASE_URL}/api/method/merigate_entry.merigate_entry.api.merigate_api.create_merigate_entry",
            "message": "Login successful"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "login_user Error")
        return {"status": "error", "message": str(e)}        