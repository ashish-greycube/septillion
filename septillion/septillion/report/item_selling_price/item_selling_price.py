# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	roles = frappe.get_roles(frappe.session.user)
	if "Sales Manager" in roles:
		canEdit = True
	else: 
		canEdit = False

	if not filters: filters = {}

	columns, data = [], []

	columns = get_columns(canEdit)
	
	data = get_items_data(filters)

	return columns, data


def get_columns(canEdit):
	return [
		{
			"fieldname": "item_image",
			"fieldtype": "HTML",
			"label": _("Item Picture"),
			"width": 120
		},
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": _("Item Code"),
			"options": "Item",
			"width": 200
		},
		{
			"fieldname": "item_name",
			"fieldtype": "Data",
			"label": _("Item Name"),
			"width": 200
		},
		{
			"fieldname": "description",
			"fieldtype": "Text",
			"label": _("Description"),
			"width": 230
		},
		{
			"fieldname": "stock_sep_qty",
			"fieldtype": "Float",
			"label": _("Stock SEP QTY"),
			"width": 130
		},
		{
			"fieldname": "exc_vat_price",
			"fieldtype": "Currency",
			"label": _("Price(Ex. VAT)"),
			"precision" : 2,
			"width": 130
		},
		{
			"fieldname": "inc_vat_price",
			"fieldtype": "Currency",
			"label": _("Price(Inc. VAT)"),
			"precision" : 2,
			"width": 130
		},
		{
			"fieldname": "max_discount",
			"fieldtype": "Float",
			"label": _("Max Discount(%)"),
			"precision" : 2,
			"editable" : canEdit,
			"focusable": True,
			"width": 110
		},
		{
			"fieldname": "exc_vat_discount_price",
			"fieldtype": "Currency",
			"label": _("Discount Price(Ex. VAT)"),
			"precision" : 2,
			"width": 150
		},
		{
			"fieldname": "inc_vat_discount_price",
			"fieldtype": "Currency",
			"label": _("Discount Price(Inc. VAT)"),
			"precision" : 2,
			"width": 150
		},
	]


def get_items_data(filters):
	conditions = get_conditions(filters)
	data = []

	default_selling_price_list = frappe.db.get_single_value('Selling Settings', 'selling_price_list')
	
	default_warehouse = frappe.db.get_single_value('Stock Settings', 'default_warehouse')

	# Getting VAT Amount
	vat_label = frappe.db.get_value(doctype = "Sales Taxes and Charges Template", filters = {"is_default" : 1})
	vat_amount = frappe.db.get_value(doctype = "Sales Taxes and Charges", filters = {"parent" : vat_label}, fieldname = ['rate'])
	
	items = frappe.get_all(
		doctype = "Item",
		fields = ['image', 'item_code', 'item_name', 'description', 'max_discount'],
		filters = conditions,
		order_by = "item_code"
	)

	stock_qty = ""
	stock_price = ""
	price_with_vat = ""
	price_in_disc_exc_vat = ""
	price_in_disc_in_vat = ""

	for item in items:
		# Setting Stock Quantity
		stock_qty = frappe.db.get_value(doctype = "Bin" ,filters = {"item_code": item.item_code, "warehouse": default_warehouse}, fieldname = ['actual_qty'])
		if stock_qty == None:
			stock_qty = 0

		# Setting Price Exc VAT
		stock_price = frappe.db.get_value(doctype = "Item Price", filters = {"item_code": item.item_code, "price_list": default_selling_price_list}, fieldname = ['price_list_rate'])
		if stock_price == None:
			stock_price =  0.00
	
		# Setting Price Inc VAT
		price_with_vat = stock_price + (stock_price * vat_amount / 100)

		# Setting Discount Price Exc VAT
		price_in_disc_exc_vat = stock_price - (stock_price * item.max_discount / 100)
		
		# Setting Discount Price Inc VAT
		price_in_disc_in_vat = price_with_vat - (price_with_vat * item.max_discount / 100)

		row  = frappe._dict({
			"item_image" : '<img src ="{0}" alt = "{1}" width = "100" height="100" class="item-image">'.format(item.image, item.item_name),
			"item_code": item.item_code,
			"item_name": item.item_name,
			"description": item.description,
			"stock_sep_qty" : stock_qty,
			"exc_vat_price" : stock_price,
			"inc_vat_price" : price_with_vat,
			"max_discount" : item.max_discount,
			"exc_vat_discount_price" : price_in_disc_exc_vat,
			"inc_vat_discount_price": price_in_disc_in_vat,
		})
		data.append(row)

	return data

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value
	return conditions

@frappe.whitelist()
def change_to_max_discount(document_code, value):
	frappe.db.set_value("Item", document_code, 'max_discount', value)
	frappe.msgprint("Max Discount is Updated in {0}".format(document_code), alert=True)	