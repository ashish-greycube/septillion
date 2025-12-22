import frappe

@frappe.whitelist()
def update_modified_time_based_on_save_of_communication_receive(self, method=None):
    if self.sent_or_received == "Received":
        received_time = self.creation
        if self.reference_doctype and self.reference_name:
           if frappe.db.exists(self.reference_doctype, self.reference_name):
               frappe.db.set_value(self.reference_doctype, self.reference_name, "modified", received_time)