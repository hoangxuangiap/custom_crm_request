
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = []

        for original_vals in vals_list:
            vals = dict(original_vals)
            opportunity_id = vals.get("opportunity_id")

            if opportunity_id and not vals.get("order_line"):
                opportunity = self.env["crm.lead"].browse(
                    opportunity_id
                ).exists()

                if opportunity:
                    order_lines = []

                    for request_line in opportunity.request_ids:
                        order_lines.append(
                            (0, 0, {
                                "product_id": (
                                    request_line.product_id
                                    .product_variant_id.id
                                ),
                                "product_uom_qty": request_line.qty,
                            })
                        )

                    if order_lines:
                        vals["order_line"] = order_lines

            prepared_vals_list.append(vals)

        return super().create(prepared_vals_list)
