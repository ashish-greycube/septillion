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
			else if (columnsList[column]['fieldname'] == "item_name") {
				item_name_col_id = column
			}
			else if (columnsList[column]['fieldname'] == "item_code") {
				item_code_col_id = column
			}
			else if (columnsList[column]['fieldtype'] == "Image" || ((columnsList[column]['fieldtype'] == "HTML") && (columnsList[column]['fieldname'] == "item_image"))) {
				parentClassName = `.dt-cell__content--col-${column}`;
				columnClassName = `.dt-cell--col-${column}, dt-cell--${column}-0`;
			}
		}




		// Image Preview Logic

		$(parentClassName).css({
			"overflow": "visible",
			"z-index": "1000"
		})

		$(".vrow").css("overflow", "hidden")



		$(document).ready(function () {

			$(".report-wrapper").on('change', `.dt-cell--col-${max_discount_col_id}, dt-cell--${max_discount_col_id}-0`, function (event) {
				current_col = event.currentTarget.dataset.colIndex
				current_row = event.currentTarget.dataset.rowIndex
				console.log(event);

				console.log(current_col, current_row);

				let cell_max_discount, cell_item_name;

				
				setTimeout(() => {
					cell_item_name = frappe.query_report.datatable.datamanager.getCell(item_name_col_id, current_row).content
					cell_max_discount = frappe.query_report.datatable.datamanager.getCell(max_discount_col_id, current_row).content
					cell_item_code = frappe.query_report.datatable.datamanager.getCell(item_code_col_id, current_row).content

					return frappe.call({
						method: "septillion.septillion.report.item_selling_price.item_selling_price.change_to_max_discount",
						args: {
							msg: "Updating Document Value",
							doctype: "Item",
							document: cell_item_name,
							document_code: cell_item_code,
							value: cell_max_discount
						},
						callback: function () {
							frappe.query_report.refresh()
						}
					});

				}, 100);

			})

			$(".report-wrapper").on('mouseenter', ".item-image", function (event) {

				$(columnClassName).hover(

					function (event) {

						total_rows = frappe.query_report.datatable.datamanager.rowCount,
							curr_row = event.currentTarget.dataset.rowIndex

						$(this).css({
							"overflow": "visible",
							"transition": "all 0.3s",
							"z-index": "998",
							"cursor": "pointer",
							"position": "relative",
						})

						if (curr_row < 6) {
							$(this).find("img").css({
								"transform": "scale(3) translateY(50%)",
								"transition": "all 0.3s",
								"cursor": "pointer",
								"position": "absolute",
								"z-index": "1000",
								"left": "50px",
								"margin": "0",
							})
						}
						else if (curr_row > total_rows - 8) {
							$(this).find("img").css({
								"transform": "scale(3) translateY(-75%)",
								"transition": "all 0.3s",
								"cursor": "pointer",
								"position": "absolute",
								"z-index": "1000",
								"left": "50px",
								"margin": "0",
							})
						}
						else {
							$(this).find("img").css({
								"transform": "scale(3)",
								"transition": "all 0.3s",
								"cursor": "pointer",
								"position": "absolute",
								"z-index": "1000",
								"left": "50px",
								"margin": "0",
							})
						}

						$(this).closest(".vrow").css("overflow", "visible")
					},

					function (event) {
						$(columnClassName).css({
							"transition": "all 0.3s",
							"z-index": "0",
							"transform": "scale(1)"
						})

						$(this).find("img").css({
							"transform": "scale(1) translateY(0)",
							"transition": "all 0.3s",
							"position": "relative",
							"z-index": "1",
							"left": "0",
						})
					}
				)
			})
		});
	}
};
