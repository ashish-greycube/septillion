import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrate():
    custom_fields = {
       "Item" : [
           {
               "fieldname": "custom_landed_cost",
               "fieldtype": "Currency",
               "label": "Landed Cost(Ex. VAT)",
               "insert_after": "max_discount",
               "is_custom_field": 1,
               "is_system_generated": 0,
           }
        ]
    }



    print("Add Expense Account For Cleaning custom table in Company and Washing Priority custom field in SI,SO.....")
    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)