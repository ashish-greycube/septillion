// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Landed Cost"] = {
	"filters": [
		{
			"fieldname": "name",
			"fieldtype": "Link",
			"label": __("Item"),
			"options": "Item",
			"reqd" : 1
		},
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": __("From Date"),
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
			"default": 'Today'
		}
	]
};
