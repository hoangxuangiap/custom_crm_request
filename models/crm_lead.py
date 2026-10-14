
from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = "crm.lead"

    request_ids = fields.One2many(
        comodel_name="crm.customer.request",
        inverse_name="opportunity_id",
        string="Nhu cầu của KH",
        copy=True,
    )

    request_sales_qty = fields.Float(
        string="Doanh số (số lượng)",
        compute="_compute_request_totals",
        store=True,
    )

    request_revenue = fields.Monetary(
        string="Doanh thu mong đợi từ nhu cầu",
        compute="_compute_request_totals",
        store=True,
        currency_field="company_currency",
    )

    @api.depends(
        "request_ids",
        "request_ids.qty",
        "request_ids.product_id",
        "request_ids.product_id.list_price",
    )
    def _compute_request_totals(self):
        for lead in self:
            lead.request_sales_qty = sum(
                lead.request_ids.mapped("qty")
            )

            lead.request_revenue = sum(
                request.qty * request.product_id.list_price
                for request in lead.request_ids
            )

    def _is_request_editable(self):
        self.ensure_one()

        # Cách nhận diện giai đoạn ban đầu theo tên.
        # Điều chỉnh nếu CRM của bạn dùng tên khác.
        if not self.stage_id:
            return True

        stage_name = (self.stage_id.name or "").strip().casefold()

        return stage_name in {"new", "mới"}

    def action_open_request_import(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Import nhu cầu khách hàng",
            "res_model": "crm.request.import.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_opportunity_id": self.id,
            },
        }
