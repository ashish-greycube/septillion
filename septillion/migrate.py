import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrate():
    custom_fields = {
       "Item" : [
           {
               "fieldname": "custom_landed_cost",
               "fieldtype": "Currency",
               "label": "Latest Landed Cost",
               "insert_after": "max_discount",
               "is_custom_field": 1,
               "is_system_generated": 0,
               "read_only" : 1
           }
        ],
        "Purchase Order Item" : [
           {
               "fieldname": "custom_landed_cost",
               "fieldtype": "Currency",
               "label": "Landed Cost",
               "insert_after": "base_price_list_rate",
               "is_custom_field": 1,
               "is_system_generated": 0,
           }
        ]
    }



    print("Adding Landed Cost custom field in Item.....")
    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)