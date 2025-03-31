// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Item Selling Price"] = {

	"filters": [
		{
			"fieldname": "name",
			"fieldtype": "Link",
			"label": __("Item"),
			"options": "Item"
		},
		{
			"fieldname": "item_group",
			"fieldtype": "Link",
			"label": __("Item Group"),
			"options": "Item Group"
		},
		{
			"fieldname": "brand",
			"fieldtype": "Link",
			"label": __("Brand"),
			"options": "Brand"
		}
	],

	get_datatable_options(options) {
		return Object.assign(options, {
			dynamicRowHeight: true,
		})
	},


	after_datatable_render: function (report) {

		columnsList = frappe.query_report.datatable.datamanager.columns;
		for (column in columnsList) {
			if (columnsList[column]['fieldname'] == "max_discount") {
				max_discount_col_id = column;
			}
			else if (columnsList[column]['fieldname'] == "item_code") {
				item_code_col_id = column
			}
			else if (columnsList[column]['fieldtype'] == "Image" || ((columnsList[column]['fieldtype'] == "HTML") && (columnsList[column]['fieldname'] == "item_image"))) {
				parentClassName = `.dt-cell__content--col-${column}`;
				columnClassName = `.dt-cell--col-${column}, dt-cell--${column}-0`;
			}
		}

		$(document).ready(function () {

			// Max-discount field logic for updating value in Item Doctype
			for (let row = 0; row <= frappe.query_report.datatable.datamanager.rowCount; row++) {
				$(".report-wrapper").off('change', `.dt-cell--col-${max_discount_col_id}, dt-cell--${max_discount_col_id}-${row}`);
				$(".report-wrapper").on('change', `.dt-cell--col-${max_discount_col_id}, dt-cell--${max_discount_col_id}-${row}`, function (event) {

					setTimeout(() => {
						if (event.currentTarget.dataset.rowIndex == row) {

							cell_max_discount = frappe.query_report.datatable.datamanager.getCell(max_discount_col_id, event.currentTarget.dataset.rowIndex).content
							cell_item_code = frappe.query_report.datatable.datamanager.getCell(item_code_col_id, event.currentTarget.dataset.rowIndex).content
							
							let typeOfValue = Number(cell_max_discount)
							if (isNaN(typeOfValue) || typeOfValue == 0) {
								cell_max_discount = 0;
							}

							return frappe.call({
								method: "septillion.septillion.report.item_selling_price.item_selling_price.change_to_max_discount",
								args: {
									msg: "Updating Document Value",
									document_code: cell_item_code,
									value: cell_max_discount,
								},
								callback: function () {
									frappe.query_report.refresh()
								}
							});
						}
					}, 100);
				})
			}

			// Item Image field logic for Zoom Image on Hovering

			$(parentClassName).css({
				"overflow": "visible",
				"z-index": "1000",
			})

			$(".vrow").css("overflow", "hidden")

			$(".report-wrapper").on('mouseenter', ".item-image", function (event) {

				$(columnClassName).hover(

					function (event) {

						total_rows = frappe.query_report.datatable.datamanager.rowCount,
						curr_row = event.currentTarget.dataset.rowIndex

						$(this).css({
							"overflow": "visible",
							"transition": "all 0.3s",
							"z-index": "999",
							"cursor": "pointer",
							"position": "relative",
						})

						if (total_rows == 1) {
							$(this).find("img").css({
								"transform": "scale(1.6) translateY(-25%)",
								"transition": "all 0.3s",
								"cursor": "pointer",
								"position": "absolute",
								"z-index": "1000",
								"left": "80px",
								"margin": "0",
								"background-color": "white"
							})

							$(".dt-scrollable").css({
								"overflow" : "visible"
							})

							$(".datatable").css({
								"overflow" : "visible"
							})
						}
						else if (curr_row < 6) {
							$(this).find("img").css({
								"transform": "scale(2) translateY(55%)",
								"transition": "all 0.3s",
								"cursor": "pointer",
								"position": "absolute",
								"z-index": "1000",
								"left": "80px",
								"margin": "0",
								"background-color": "white"
							})
						}
						else if (curr_row > total_rows - 12) {
							$(this).find("img").css({
								"transform": "scale(2) translateY(-75%)",
								"transition": "all 0.3s",
								"cursor": "pointer",
								"position": "absolute",
								"z-index": "1000",
								"left": "80px",
								"margin": "0",
								"background-color": "white"
							})
						}
						else {
							$(this).find("img").css({
								"transform": "scale(2) translateY(35%)",
								"transition": "all 0.3s",
								"cursor": "pointer",
								"position": "absolute",
								"z-index": "1000",
								"left": "80px",
								"margin": "0",
								"background-color": "white"
							})
						}

						$(this).closest(".vrow").css("overflow", "visible")
					},

					function (event) {
						$(columnClassName).css({
							"transition": "all 0.3s",
							"z-index": "1",
							"position": "relative",
							"transform": "scale(1)"
						})

						$(this).find("img").css({
							"overflow" : "hidden",
							"transform": "scale(1)",
							"transition": "all 0.3s",
							"position": "relative",
							"z-index": "-1",
							"left": "0",
						})

						if (total_rows == 1) {
							$(this).closest(".vrow").css("overflow", "hidden")
							$(".dt-scrollable").css({
								"overflow" : "hidden"
							})
						}	
					}
				)
			})
		});
	}
};