// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Landed Movement"] = {
	"filters": [
		{
			"fieldname": "name",
			"fieldtype": "Link",
			"label": __("Item"),
			"options": "Item",
			"reqd": 1,
		}
	],

	get_datatable_options(options) {
		
		return Object.assign(options, {
			dynamicRowHeight: true
		});
	},

	after_datatable_render: function (report) {
		columnsList = frappe.query_report.datatable.datamanager.columns;
		for (column in columnsList) {
			if (columnsList[column]['fieldname'] == "safety_stock_qty") {
				safety_stock_col_id = column;
			}
		}

		$(`.dt-cell--col-${safety_stock_col_id}, dt-cell--${safety_stock_col_id}-0`).on("change", function (event) {
			current_col = event.currentTarget.dataset.colIndex
			current_row = event.currentTarget.dataset.rowIndex
			

			let cell_safety_stock;
			
			setTimeout(() => {
				cell_safety_stock = frappe.query_report.datatable.datamanager.getCell(safety_stock_col_id, current_row).content
				
				return frappe.call({
					method: "septillion.septillion.report.landed_movement.landed_movement.change_to_safety_stock",
					args: {
						msg: "Updating Document Value",
						doctype: "Item",
						document: frappe.query_report.filters[0].value,
						value: cell_safety_stock
					},
					callback: function () {
						frappe.query_report.refresh()
					}
				});

			}, 100);
		});
	}
};