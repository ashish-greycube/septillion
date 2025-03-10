# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from frappe.utils import add_to_date


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
			"months" : record.get('month'),
			"buy_in" : record.get('inQty'),
			"sell_out" : record.get('outQty'),
			"end_of_month_stock" : record.get('endQty'),
			"safety_stock_qty" : record.get('safetyStock')
		})

		data.append(row)
	
	chart = get_chart(data)

	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "months",
			"fieldtype": "Data",
			"label" : _("Months"),
			"width" : 150
		},
		{
			"fieldname" : "buy_in",
			"fieldtype" : "Float",
			"label" : _("Buy In(Stock Received)"),
			"precision" : 2,
			"width" : 180,
		},
		{
			"fieldname" : "sell_out",
			"fieldtype" : "Float",
			"label" : _("Sell Out(Delivery Note)"),
			"precision" : 2,
			"width" : 180,
		},
		{
			"fieldname" : "end_of_month_stock",
			"fieldtype" : "Float",
			"label" : _("End of Month Stock"),
			"precision" : 2,
			"width" : 180,
		},
		{
			"fieldname" : "safety_stock_qty",
			"fieldtype" : "Float",
			"label" : _("Safety Stock Qty"),
			"editable" : True,
			"precision" : 2,
			"width" : 180,
		},
	]


def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value
	return conditions


def get_records(filters):
	conditions = get_conditions(filters)
	data = []
	for i in range(24):
		formattedMonth = add_to_date(datetime.now(), months = -i).strftime("%b-%Y")
		month = add_to_date(datetime.now(), months = -i).strftime("%m")
		year = add_to_date(datetime.now(), months = -i).strftime("%Y")

		stockIn_qty = frappe.db.sql("""
								SELECT IFNULL (SUM(tsle.actual_qty), 0) as 'In Qty'
								FROM `tabStock Ledger Entry` tsle 
								WHERE tsle.item_code = '{0}'
								AND tsle.warehouse = 'Stocks - SEP'
								AND tsle.actual_qty > 0
								AND tsle.is_cancelled = 0
								AND tsle.posting_date BETWEEN '{1}-{2}-01' AND '{1}-{2}-31';
							""".format(conditions.get('name'), year, month),
							as_dict = 1)
		

		stockOut_qty = frappe.db.sql("""
								SELECT IFNULL(SUM(tsle.actual_qty), 0) AS 'Out Qty'
								FROM `tabStock Ledger Entry` tsle 
								WHERE tsle.item_code = '{0}'
								AND tsle.warehouse = 'Stocks - SEP'
								AND tsle.actual_qty < 0
								AND tsle.is_cancelled = 0
								AND tsle.posting_date BETWEEN '{1}-{2}-01' AND '{1}-{2}-31';
							""".format(conditions.get('name'), year, month),
							as_dict = 1)
		

		endBalance_qty = frappe.db.sql("""
								SELECT tsle.qty_after_transaction AS 'Balance Qty'
								FROM `tabStock Ledger Entry` tsle 
								WHERE tsle.item_code = '{0}'
								AND tsle.warehouse = 'Stocks - SEP'
								AND tsle.is_cancelled = 0 
								AND tsle.posting_date BETWEEN '{1}-{2}-01' AND '{1}-{2}-31'
								ORDER BY tsle.posting_datetime   DESC 
								LIMIT 1;
							""".format(conditions.get('name'), year, month),
							as_dict = 1)
		

		if len(endBalance_qty) == 0:
			
			tempMonth = month
			tempYear = year
			
			while len(endBalance_qty) != 1 :
				
				prevMonth = add_to_date(datetime.strptime("{0}-{1}-01".format(tempYear, tempMonth), "%Y-%m-%d") , months = -1).strftime("%m")
				prevYear = add_to_date(datetime.strptime("{0}-{1}-01".format(tempYear, tempMonth), "%Y-%m-%d") , months = -1).strftime("%Y")
				
				if (prevYear == add_to_date(datetime.now(), months = -48).strftime("%Y")) and (prevMonth == add_to_date(datetime.now(), months = -24).strftime("%m")):
					endBalance_qty = 0
					break
					
				newEndBalance_qty = frappe.db.sql("""
								SELECT tsle.qty_after_transaction AS 'Balance Qty'
								FROM `tabStock Ledger Entry` tsle 
								WHERE tsle.item_code = '{0}'
								AND tsle.warehouse = 'Stocks - SEP'
								AND tsle.is_cancelled = 0 
								AND tsle.posting_date BETWEEN '{1}-{2}-01' AND '{1}-{2}-31'
								ORDER BY tsle.posting_datetime DESC 
								LIMIT 1;
							""".format(conditions.get('name'), prevYear, prevMonth),
							as_dict = 1)

				endBalance_qty = newEndBalance_qty

				tempMonth = prevMonth 
				tempYear = prevYear

		if endBalance_qty != 0:
			endBalance_qty = endBalance_qty[0]['Balance Qty']

		row_data = ({
			"month" : formattedMonth,
			"inQty" : stockIn_qty[0]['In Qty'],
			"outQty": stockOut_qty[0]['Out Qty'] - (2 * stockOut_qty[0]['Out Qty']),
			"endQty": endBalance_qty,
			"safetyStock" : frappe.db.get_value(
				doctype = "Item",
				filters = {'item_code': conditions.get('name')},
				fieldname = ['safety_stock']  )
		})
		data.append(row_data)

	return data	


def get_chart(records):
	if not records:
		return None
	
	labels = []
	buy_in_values = []
	sell_out_values = []
	end_stock_values = []
	safety_stock_values = []

	for record in records:
		labels.append(record.months)
		buy_in_values.append(record.buy_in)
		sell_out_values.append(record.sell_out)
		end_stock_values.append(record.end_of_month_stock)
		safety_stock_values.append(record.safety_stock_qty)

	chart = {
		'title': "Landed Movement Chart",
		'data' : {
			'labels': labels,
			'datasets' : [
				{
					'name': "Buy In Stock",
        			'values': buy_in_values,
        			'chartType': 'bar',
				},
				{
					'name': "Sell Out Stock",
        			'values': sell_out_values,
        			'chartType': 'bar'
				},
				{
					'name': "Month End Stock",
        			'values': end_stock_values,
        			'chartType': 'line'
				},
				{
					'name': "Safety Stock Value",
        			'values': safety_stock_values,
        			'chartType': 'line'
				},
			],
		},
		"colors": ["#FFDF00", "#9A7B4F","#FF0000", "#2196F3"],
	}
	return chart

@frappe.whitelist()
def change_to_safety_stock(doctype, document, value, msg):
	item_id = frappe.get_all(doctype, filters = {"name" : document})
	doc = frappe.get_doc(doctype, item_id)
	doc.safety_stock = value
	doc.save()