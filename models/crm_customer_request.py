
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class CrmCustomerRequest(models.Model):
    _name = "crm.customer.request"
    _description = "Customer Request"
    _order = "date desc, id desc"

    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Sản phẩm",
        required=True,
        ondelete="restrict",
    )

    opportunity_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Cơ hội",
        required=True,
        ondelete="cascade",
        index=True,
    )

    date = fields.Date(
        string="Ngày yêu cầu",
        required=True,
        default=fields.Date.context_today,
    )

    description = fields.Text(
        string="Mô tả",
    )

    qty = fields.Float(
        string="Số lượng",
        required=True,
        default=1.0,
    )

    unit_price = fields.Monetary(
        string="Đơn giá",
        compute="_compute_amount",
        currency_field="currency_id",
        store=True,
    )

    amount = fields.Monetary(
        string="Thành tiền",
        compute="_compute_amount",
        currency_field="currency_id",
        store=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="opportunity_id.company_currency",
        string="Tiền tệ",
        readonly=True,
    )

    @api.depends(
        "qty",
        "product_id",
        "product_id.list_price",
    )
    def _compute_amount(self):
        for request in self:
            if request.product_id:
                request.unit_price = request.product_id.list_price
                request.amount = (
                    request.qty * request.product_id.list_price
                )
            else:
                request.unit_price = 0.0
                request.amount = 0.0

    @api.constrains("qty")
    def _check_qty(self):
        for request in self:
            if request.qty <= 0:
                raise ValidationError(
                    _("Số lượng yêu cầu phải lớn hơn 0.")
                )

    def _check_opportunity_editable(self):
        for request in self:
            if not request.opportunity_id._is_request_editable():
                raise UserError(
                    _(
                        "Chỉ được thêm, sửa hoặc xóa nhu cầu "
                        "khi cơ hội đang ở trạng thái Mới."
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        requests = super().create(vals_list)
        requests._check_opportunity_editable()
        return requests

    def write(self, vals):
        self._check_opportunity_editable()
        return super().write(vals)

    def unlink(self):
        self._check_opportunity_editable()
        return super().unlink()
