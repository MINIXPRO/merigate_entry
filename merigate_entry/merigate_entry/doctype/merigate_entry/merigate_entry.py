import frappe
from frappe.model.document import Document


class MerigateEntry(Document):
    def on_doctype_update(self):
        pass
