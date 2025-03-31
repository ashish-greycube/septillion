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
	],



	after_datatable_render: function (report) {

		columnsList = frappe.query_report.datatable.datamanager.columns;
		for (column in columnsList) {
			if (columnsList[column]['fieldname'] == "landed_cost") {
				custom_landed_cost_col_id = column;
			}
			else if (columnsList[column]['fieldname'] == "purchase_order") {
				purchase_order_col_id = column;
			}
		}

		$(document).ready(function () {
			
			// Landed Cost field logic for updating value in Purchase Order Doctype
			for (let row = 0; row <= frappe.query_report.datatable.datamanager.rowCount; row++) {
				$(".report-wrapper").off('change', `.dt-cell--col-${custom_landed_cost_col_id}, dt-cell--${custom_landed_cost_col_id}-${row}`);
				$(".report-wrapper").on('change', `.dt-cell--col-${custom_landed_cost_col_id}, dt-cell--${custom_landed_cost_col_id}-${row}`, function (event) {

					setTimeout(() => {
						if (event.currentTarget.dataset.rowIndex == row) {
							
							cell_landed_cost = frappe.query_report.datatable.datamanager.getCell(custom_landed_cost_col_id, row).content
							cell_purchase_order = frappe.query_report.datatable.datamanager.getCell(purchase_order_col_id, row).content
							cell_db_name = frappe.query_report.data[row].db_po_name

							let typeOfValue = Number(cell_landed_cost)
							if (isNaN(typeOfValue) || typeOfValue == 0) {
								cell_landed_cost = 0;
							}

							return frappe.call({
								method: "septillion.septillion.report.landed_cost.landed_cost.set_landed_cost_in_purchase_order",
								args: {
									msg: "Updating Document Value",
									document_code: cell_purchase_order,
									value: cell_landed_cost,
									item_code: frappe.query_report.filters[0].value,
									po_db_name : cell_db_name
								},
								callback: function () {
									frappe.query_report.refresh()
								}
							});
						}
					}, 100);
				})
			}
		});
	}
};
