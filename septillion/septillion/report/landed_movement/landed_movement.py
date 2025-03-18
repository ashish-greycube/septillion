# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from frappe.utils import add_to_date, month_diff

def execute(filters=None):
	roles = frappe.get_roles(frappe.session.user)
	if "Purchase Manager" in roles:
		canEdit = True
	else:
		canEdit = False

	if not filters : filters = {}

	columns, data = [], []

	columns = get_columns(canEdit)
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

		message = None
		if record.get('msg'):
			message = '''
				<div class="alert alert-info alert-dismissible fade show" role="alert">
					{0}
					<button type="button" class="close" data-dismiss="alert" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
				'''.format(record.get('msg'))
		
	
	chart = get_chart(data)	

	return columns, data, message, chart


def get_columns(canEdit):
	return [
		{
			"fieldname": "months",
			"fieldtype": "Data",
			"label" : _("Months"),
			"width" : 130
		},
		{
			"fieldname" : "buy_in",
			"fieldtype" : "Float",
			"label" : _("Buy In(Stock Received)"),
			"precision" : 2,
			"width" : 130,
		},
		{
			"fieldname" : "sell_out",
			"fieldtype" : "Float",
			"label" : _("Sell Out(Delivery Note)"),
			"precision" : 2,
			"width" : 130,
		},
		{
			"fieldname" : "end_of_month_stock",
			"fieldtype" : "Float",
			"label" : _("End of Month Stock"),
			"precision" : 2,
			"width" : 130,
		},
		{
			"fieldname" : "safety_stock_qty",
			"fieldtype" : "Float",
			"label" : _("Safety Stock Qty"),
			"editable" : canEdit,
			"precision" : 2,
			"width" : 130,
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
	current_item = conditions.get('name')

	# First Entry of That Item in Warehouse
	item_creation = frappe.db.sql("""
				SELECT DATE_FORMAT(tsle.posting_datetime, '%Y-%m') as 'creation_date'
				FROM `tabStock Ledger Entry` as tsle 
				WHERE tsle.item_code = '{0}'
				AND tsle.warehouse = 'Stocks - SEP'
				ORDER BY tsle.posting_datetime ASC
				LIMIT 1;		
	""".format(current_item), as_dict = 1)

	# Report Last Date (Before 24 Months From Now)
	reportLastDate = add_to_date(datetime.now(), months = -23).strftime('%Y-%m') 

	# Main Logic - If Item Does not have any entry yet
	if len(item_creation) == 0:
		for i in range(23, -1, -1):
			formattedMonth = add_to_date(datetime.now(), months = -i).strftime("%b-%Y")
			row_data = ({
				"month" : formattedMonth,
				"inQty" : 0,
				"outQty" : 0,
				"endQty" : 0,
				"safetyStock" : frappe.db.get_value(
					doctype = "Item",
					filters = {'item_code': current_item},
					fieldname = ['safety_stock']),
				"msg" : "There is no buy or sell entry for this item."
			})

			data.append(row_data)
		data = data[::-1]


	# Main Logic - If Item is Created Before Report Last Date
	elif item_creation[0]['creation_date'] < reportLastDate:
		prev_bal = frappe.db.sql("""
						SELECT tsle.qty_after_transaction as 'previous_stock'
						FROM `tabStock Ledger Entry` as tsle 
						WHERE tsle.item_code = '{0}'
						AND tsle.warehouse = 'Stocks - SEP'
						ORDER BY tsle.posting_datetime ASC
						LIMIT 1;
						""".format(current_item), as_dict = 1)
		
		bal_qty = 0.0
		prev_bal_qty =  prev_bal[0]['previous_stock']

		month_difference = month_diff(reportLastDate, item_creation[0]['creation_date'])

		for i in range(month_difference - 1):
			cur_year = add_to_date(datetime.strptime("{0}-01".format(item_creation[0]['creation_date']), "%Y-%m-%d"), months = i).strftime("%Y")
			cur_month = add_to_date(datetime.strptime("{0}-01".format(item_creation[0]['creation_date']), "%Y-%m-%d"), months = i).strftime("%m")
				
			item_entries = frappe.db.sql("""
						SELECT tsle.actual_qty
						FROM `tabStock Ledger Entry` as tsle
						WHERE tsle.item_code = '{2}'
						AND tsle.warehouse = 'Stocks - SEP'
						AND tsle.is_cancelled = 0
						AND tsle.posting_date BETWEEN '{0}/{1}/01' AND '{0}/{1}/31'
						ORDER BY tsle.posting_datetime;
			""".format(cur_year, cur_month, current_item), as_dict = 1)

			# Calculatig item in and out qty of that month
			in_qty = 0.0
			out_qty = 0.0
			for entry in item_entries:
				if entry['actual_qty'] > 0:
					in_qty += entry['actual_qty']
				else:
					out_qty += entry['actual_qty']
			
			# Calculating Balance Qty of That Month
			if i == 0 and in_qty == prev_bal_qty:
				bal_qty = in_qty + out_qty
			else:
				bal_qty = (prev_bal_qty + in_qty) + out_qty

			# Setting Previous Balance Qty For Further Use
			prev_bal_qty = bal_qty

		for i in range(23, -1, -1):
			cur_month = add_to_date(datetime.now(), months = -i).strftime("%m")
			cur_year = add_to_date(datetime.now(), months = -i).strftime("%Y")
			cur_frm_date = add_to_date(datetime.now(), months = -i).strftime("%Y-%m")
			formattedMonth = add_to_date(datetime.now(), months = -i).strftime("%b-%Y")

			# Fetching Item Data for Specific Month
			item_entries = frappe.db.sql("""
						SELECT tsle.actual_qty
						FROM `tabStock Ledger Entry` as tsle
						WHERE tsle.item_code = '{2}'
						AND tsle.warehouse = 'Stocks - SEP'
						AND tsle.is_cancelled = 0
						AND tsle.posting_date BETWEEN '{0}/{1}/01' AND '{0}/{1}/31'
						ORDER BY tsle.posting_datetime;
			""".format(cur_year, cur_month, current_item), as_dict = 1)

			# Calculatig item in and out qty of that month
			in_qty = 0.0
			out_qty = 0.0
			for entry in item_entries:
				if entry['actual_qty'] > 0:
					in_qty += entry['actual_qty']
				else:
					out_qty += entry['actual_qty']
			
			# Calculating Balance Qty of That Month
			bal_qty = (prev_bal_qty + in_qty) + out_qty

			# Setting Previous Balance Qty For Further Use
			prev_bal_qty = bal_qty 

			row_data = ({
				"month" : formattedMonth,
				"inQty" : in_qty,
				"outQty" : out_qty - (2 * out_qty),
				"endQty" : bal_qty,
				"safetyStock" : frappe.db.get_value(
					doctype = "Item",
					filters = {'item_code': current_item},
					fieldname = ['safety_stock'])
			})
		
			data.append(row_data)
		data = data[::-1]

	# If Item is Created After Report Last Date
	elif item_creation[0]['creation_date'] >= reportLastDate:
		bal_qty = 0.0
		prev_bal_qty = 0.0
		
		for i in range(23, -1, -1):
			cur_month = add_to_date(datetime.now(), months = -i).strftime("%m")
			cur_year = add_to_date(datetime.now(), months = -i).strftime("%Y")
			cur_frm_date = add_to_date(datetime.now(), months = -i).strftime("%Y-%m")
			formattedMonth = add_to_date(datetime.now(), months = -i).strftime("%b-%Y")
			
			if cur_frm_date >= reportLastDate:
				# Fetching Item Data for Specific Month
				item_entries = frappe.db.sql("""
							SELECT tsle.actual_qty
							FROM `tabStock Ledger Entry` as tsle
							WHERE tsle.item_code = '{2}'
							AND tsle.warehouse = 'Stocks - SEP'
							AND tsle.is_cancelled = 0
							AND tsle.posting_date BETWEEN '{0}/{1}/01' AND '{0}/{1}/31'
							ORDER BY tsle.posting_datetime;
				""".format(cur_year, cur_month, current_item), as_dict = 1)

				# Calculatig item in and out qty of that month
				in_qty = 0.0
				out_qty = 0.0
				for entry in item_entries:
					if entry['actual_qty'] > 0:
						in_qty += entry['actual_qty']
					else:
						out_qty += entry['actual_qty']
				
				# Calculating Balance Qty of That Month
				bal_qty = (prev_bal_qty + in_qty) + out_qty

				# Setting Previous Balance Qty For Further Use
				prev_bal_qty = bal_qty
			else:
				in_qty = 0.0
				out_qty = 0.0
				bal_qty = 0.0
				prev_bal_qty = 0.0

			row_data = ({
				"month" : formattedMonth,
				"inQty" : in_qty,
				"outQty" : out_qty - (2 * out_qty),
				"endQty" : bal_qty,
				"safetyStock" : frappe.db.get_value(
					doctype = "Item",
					filters = {'item_code': current_item},
					fieldname = ['safety_stock'])
			})
		
			data.append(row_data)
		data = data[::-1]

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
		'data' : {
			'labels': labels,
			'datasets' : [
				{
					'name': "Buy In Stock(This Color Line Will Show the Changes in Buy In Stock)",
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
def change_to_safety_stock(doctype, document, value,  msg):
	item_id = frappe.get_all(doctype, filters = {"item_code" : document})
	doc = frappe.get_doc(doctype, item_id)
	doc.safety_stock = value
	doc.save()
	frappe.msgprint("Safety Stock is Updated in {0}".format(document), alert=True)