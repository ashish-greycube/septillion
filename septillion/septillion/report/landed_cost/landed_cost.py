# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	roles = frappe.get_roles(frappe.session.user)
	if "Purchase Manager" in roles:
		canEdit = True
	else:
		canEdit = False

	if not filters : filters = {}
	columns, data = [], []

	columns = get_columns(canEdit)
	data = get_records(filters)

	if not data:
		frappe.msgprint("No Data Found")
		return columns, data

	chart = get_chart(data)
	return columns, data, None, chart


def get_columns(canEdit):
	return [
		{
			"fieldname" : "purchase_order",
			"fieldtype" : "Link",
			"label" : _("Purchase Order"),
			"options" : "Purchase Order",
			"width" : 150
		},
		{
			"fieldname" : "date",
			"fieldtype" : "Date",
			"label" : _("Date"),
			"width" : 150
		},
		{
			"fieldname" : "currency",
			"fieldtype" : "Data",
			"label" : _("Currency"),
			"width" : 100
		},
		{
			"fieldname" : "buy_price",
			"fieldtype" : "Currency",
			"label" : _("Buying Price"),
			"width" : 120
		},
		{
			"fieldname" : "exc_rate",
			"fieldtype" : "Float",
			"label" : _("Exchange Rate"),
			"width" : 120
		},
		{
			"fieldname" : "landed_cost",
			"fieldtype" : "Float",
			"label" : _("Landed Cost"),
			"editable" : canEdit,
			"width" : 120
		},
		{
			"fieldname" : "ship_vs_buy_price",
			"fieldtype" : "Percentage",
			"label" : _("Shipment Cost VS Buying Price"),
			"precision" : 2,
			"width" : 120
		},
	]

def get_records(filters):
	item = filters.get('name')
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')
	
	records = []
	purchase_data = frappe.db.sql("""
								SELECT tpo.name as po_name, tpo.transaction_date, tpo.currency , tpoi.rate, tpo.conversion_rate, tpoi.custom_landed_cost, tpoi.name as poi_name
								FROM `tabPurchase Order` as tpo INNER JOIN `tabPurchase Order Item` as tpoi
								WHERE tpoi.parent = tpo.name
								AND tpoi.item_code = '{0}'
								AND tpo.transaction_date BETWEEN '{1}' AND '{2}'
							   	ORDER BY tpo.creation DESC;
							""".format(item, from_date, to_date),
							as_dict  = 1)

	for data in purchase_data:
		if data.custom_landed_cost == 0:
			data.svb_value = 0
		else:
			data.svb_value = (data.custom_landed_cost - data.rate) / data.custom_landed_cost

		row = frappe._dict({
			"purchase_order" : data.po_name,
			"date" : data.transaction_date,
			"currency" : data.currency,
			"buy_price" : data.rate,
			"exc_rate" : data.conversion_rate,
			"landed_cost" : data.custom_landed_cost,
			"ship_vs_buy_price" : round(data.svb_value, 2),
			"db_po_name" : data.poi_name
		})
		
		records.append(row)
	return records

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value

	return conditions

def get_chart(data):
	if not data:
		frappe.msgprint("There is no Data Available")
	
	labels = []
	buying_prices = []
	landed_costs = []
	exchange_rates = []

	for dt in data:
		labels.append(dt.date)
		buying_prices.append(dt.buy_price)
		landed_costs.append(dt.landed_cost)
		exchange_rates.append(dt.exc_rate)

	labels = labels[::-1]
	buying_prices = buying_prices[::-1]
	landed_costs = landed_costs[::-1]
	exchange_rates = exchange_rates[::-1]
	
	chart = {
		'data': {
			'labels': labels,
			'datasets' : [
				{
					'name' : "Buying Price",
					'values' : buying_prices
				},
				{
					'name' : "Landed Cost",
					'values' : landed_costs
				},
				{
					'name' : "Exchange Rate",
					'values' : exchange_rates
				}
			],
		},
		'type' : 'line',
		'colors': ['#0ae500', '#ff0000', '#7f00ff']
	}

	return chart


def set_latest_landed_cost_in_item(item_code):
	latest_purchase_order = frappe.db.sql("""
			SELECT tpoi.custom_landed_cost FROM `tabPurchase Order` tpo INNER JOIN `tabPurchase Order Item` tpoi 
			WHERE tpoi.item_code = '{0}'
			AND tpoi.parent  = tpo.name
			ORDER BY tpo.transaction_date DESC, tpo.name DESC, tpoi.modified DESC
			LIMIT 1;
			""".format(item_code), as_dict = 1)

	if len(latest_purchase_order) > 0:
			custom_landed_cost_value = latest_purchase_order[0].custom_landed_cost
			if custom_landed_cost_value > 0:
				frappe.db.set_value("Item", item_code, 'custom_landed_cost', custom_landed_cost_value)
				frappe.msgprint("Landed Cost is Updated in Item {0}".format(item_code), alert=True)


@frappe.whitelist()
def set_landed_cost_in_purchase_order(document_code, value, item_code, po_db_name):

	doc = frappe.get_doc("Purchase Order", document_code)

	for item in doc.items:
		if item.item_code == item_code:
			if item.name == po_db_name:
				frappe.db.set_value("Purchase Order Item", item.name, 'custom_landed_cost', value)
	frappe.msgprint("Landed Cost is Updated in PO {0}".format(document_code), alert=True)

	set_latest_landed_cost_in_item(item_code)	


@frappe.whitelist()
def change_landed_cost_on_validation(self, method):
	for row in self.items:
		item_code = row.item_code
		set_latest_landed_cost_in_item(item_code)