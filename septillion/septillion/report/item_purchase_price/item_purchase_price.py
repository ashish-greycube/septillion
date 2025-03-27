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
	
	if not filters: filters = {}

	columns, data = [], []

	columns = get_columns(canEdit)
	items_data = get_items_data(filters)

	for items in items_data:
		row  = frappe._dict({
			"item_image" : '<img src ={0} width = "100" height="100" alt = {1} class="item-image">'.format(items.image, items.item_name),
			"item_code": items.item_code,
			"item_name": items.item_name,
			"sep_qty" : items.stock_sep_qty,
			"safety_stock_qty" : items.safety_stock,
			"custom_landed_cost_ex_vat" : items.custom_landed_cost,
			"custom_landed_cost_inc_vat" : items.custom_landed_cost_inc_vat,
			"price_ex_vat" : items.price_ex_vat,
			"price_inc_vat" : items.price_inc_vat,
			"profit_amount" : items.profit_amount,
			"profit_percentage" : items.profit_percentage,
			"max_discount" : items.max_discount,
		})
		data.append(row)

	return columns, data

def get_columns(canEdit):
	return [
		{
			"fieldname" : "item_image",
			"fieldtype" : "HTML",
			"label" : _('Item Image'),
			"width" : 120
		},
		{
			"fieldname" : "item_code",
			"fieldtype" : "Link",
			"label" : _('Item Code'),
			"options" : "Item",
			"width" : 180
		},
		{
			"fieldname" : "item_name",
			"fieldtype" : "Data",
			"label" : _('Item Name'),
			"width" : 150
		},
		{
			"fieldname" : "max_discount",
			"fieldtype" : "Float",
			"label" : _('Max Discount(%)'),
			"precision" : 2,
			"editable" : canEdit,
			"width" : 120 
		},
		{
			"fieldname" : "sep_qty",
			"fieldtype" : "Float",
			"label" : _('Stock SEP Qty'),
			"precision" : 2,
			"width" : 150
		},
		{
			"fieldname" : "safety_stock_qty",
			"fieldtype" : "Float",
			"label" : _('Safety Stock Qty'),
			"editable" : canEdit,
			"precision" : 2,
			"width" : 150
		},
		{
			"fieldname" : "custom_landed_cost_ex_vat",
			"fieldtype" : "Currency",
			"label" : _('Landed Cost(Ex. VAT)'),
			"editable" : canEdit,
			"width" : 150
		},
		{
			"fieldname" : "custom_landed_cost_inc_vat",
			"fieldtype" : "Currency",
			"label" : _('Landed Cost(Inc. VAT)'),
			"width" : 150
		},
		{
			"fieldname" : "price_ex_vat",
			"fieldtype" : "Currency",
			"label" : _('Price(Ex. VAT)'),
			"width" : 150
		},
		{
			"fieldname" : "price_inc_vat",
			"fieldtype" : "Currency",
			"label" : _('Price(Inc. VAT)'),
			"width" : 150
		},
		{
			"fieldname" : "profit_amount",
			"fieldtype" : "Currency",
			"label" : _('Profit Amount'),
			"width" : 150
		},
		{
			"fieldname" : "profit_percentage",
			"fieldtype" : "Percentage",
			"label" : _('Profit (%)'),
			"width" : 100
		}
	]

def get_items_data(filters):
	conditions = get_conditions(filters)

	default_selling_price_list = frappe.db.get_single_value('Selling Settings', 'selling_price_list')
	
	default_warehouse = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
	
	# VAT Amount
	vat_label = frappe.db.get_value(doctype = "Sales Taxes and Charges Template", filters = {"is_default" : 1})
	vat_amount = frappe.db.get_value(doctype = "Sales Taxes and Charges", filters = {"parent" : vat_label}, fieldname = ['rate'])
	
	data = frappe.get_all(
			doctype = "Item",
			fields = ['image', 'item_code', 'item_name', 'safety_stock', 'custom_landed_cost',  'max_discount'],
			filters = conditions,
			order_by = "item_code"
	)
	for item in data:
		# Stock Quantity
		
		stock_qty = frappe.db.get_value(doctype = "Bin" ,filters = {"item_code": item.item_code, "warehouse": default_warehouse}, fieldname = ['actual_qty'])
		if stock_qty == None:
			item.stock_sep_qty = 0
		else:
			item.stock_sep_qty = stock_qty
		
		# Landed Cost Inc VAT
		landed_cost_with_vat = item.custom_landed_cost + (item.custom_landed_cost * vat_amount / 100)
		item.custom_landed_cost_inc_vat = landed_cost_with_vat
		
		# Price Exc VAT
		stock_price = frappe.db.get_value(doctype = "Item Price", filters = {"item_code": item.item_code, "price_list": default_selling_price_list}, fieldname = ['price_list_rate'])
		if stock_price == None:
			item.price_ex_vat =  0.00
		else:
			item.price_ex_vat = stock_price

		# # Price Inc VAT
		price_with_vat = item.price_ex_vat + (item.price_ex_vat * vat_amount / 100)
		item.price_inc_vat = price_with_vat

		# Profit Amount
		profit_amt = item.price_ex_vat - item.custom_landed_cost
		item.profit_amount = profit_amt

		# Profit Percentage
		if item.custom_landed_cost == 0: 
			profit_percent = 0
		elif(item.custom_landed_cost > 0): 
			profit_percent = profit_amt / item.custom_landed_cost

		item.profit_percentage = round(profit_percent, 2)

	return data


def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value
		
	return conditions


@frappe.whitelist()
def change_to_max_discount(document, value, document_code, msg):
	item_id = frappe.get_all("Item", filters = {"item_name" : document, "item_code" : document_code})
	frappe.db.set_value("Item", item_id, 'max_discount', value)
	frappe.msgprint("Max Discount is Updated in {0}".format(document_code), alert=True)

@frappe.whitelist()
def change_to_safety_stock(document, value, document_code, msg):
	item_id = frappe.get_all("Item", filters = {"item_name" : document, "item_code" : document_code})
	frappe.db.set_value("Item", item_id, 'max_discount', value)
	frappe.msgprint("Safety Stock is Updated in {0}".format(document_code), alert=True)

@frappe.whitelist()
def change_to_landed_cost(document, value, document_code,  msg):
	item_id = frappe.get_all("Item", filters = {"item_name" : document, "item_code" : document_code})
	frappe.db.set_value("Item", item_id, 'max_discount', value)
	frappe.msgprint("Landed Cost is Updated in {0}".format(document_code), alert=True)