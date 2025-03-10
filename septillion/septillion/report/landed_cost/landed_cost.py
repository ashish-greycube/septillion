# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters : filters = {}
	columns, data = [], []

	columns = get_columns()
	records = get_records(filters)

	if not records:
		frappe.msgprint("No Data Found")
		return columns, data
	
	for record in records:
		row = frappe._dict({
			"purchase_order" : record.name,
			"date" : record.transaction_date,
			"currency" : record.currency,
			"buy_price" : record.rate,
			"exc_rate" : record.conversion_rate,
			"landed_cost" : record.landed_cost,
			"ship_vs_buy_price" : record.svb_value
		})

		data.append(row)

		chart = get_chart(data)

	return columns, data, None, chart


def get_columns():
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
			"width" : 150
		},
		{
			"fieldname" : "buy_price",
			"fieldtype" : "Currency",
			"label" : _("Buying Price"),
			"width" : 150
		},
		{
			"fieldname" : "exc_rate",
			"fieldtype" : "Float",
			"label" : _("Exchange Rate"),
			"width" : 150
		},
		{
			"fieldname" : "landed_cost",
			"fieldtype" : "Float",
			"label" : _("Landed Cost"),
			"width" : 150
		},
		{
			"fieldname" : "ship_vs_buy_price",
			"fieldtype" : "Percentage",
			"label" : _("Shipment Cost VS Buying Price"),
			"width" : 150
		},
	]

def get_records(filters):
	conditions = get_conditions(filters)

	item = conditions.get('name')
	from_date = conditions.get('from_date')
	to_date = conditions.get('to_date')

	purchase_data = frappe.db.sql("""
								SELECT tpo.name, tpo.transaction_date, tpo.currency , tpoi.rate, tpo.conversion_rate 
								FROM `tabPurchase Order` as tpo INNER JOIN `tabPurchase Order Item` as tpoi
								WHERE tpoi.parent = tpo.name
								AND tpoi.item_code = '{0}'
								AND tpo.transaction_date BETWEEN '{1}' AND '{2}';
							""".format(item, from_date, to_date),
							as_dict  = 1)

	for data in purchase_data:
		data.landed_cost = frappe.db.get_value("Item", item, 'custom_landed_cost')

		if data.landed_cost == 0:
			data.svb_value = 0
		else:
			data.svb_value = (data.landed_cost - data.rate) / data.landed_cost

	return purchase_data

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