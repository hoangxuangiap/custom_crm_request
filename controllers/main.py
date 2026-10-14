from odoo import http, fields
from odoo.http import request


class CrmLeadApiController(http.Controller):

    @http.route(
        "/api/crm/leads",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def create_lead(self, **kwargs):
        data = request.httprequest.get_json(silent=True)

        if not isinstance(data, dict):
            return request.make_json_response(
                {"error": "Body phải là JSON object."},
                status=400,
            )

        required_fields = [
            "name",
            "customer",
            "date_deadline",
            "requests",
        ]

        missing = [
            key for key in required_fields
            if not data.get(key)
        ]

        if missing:
            return request.make_json_response(
                {
                    "error": "Thiếu trường bắt buộc.",
                    "fields": missing,
                },
                status=400,
            )

        if not isinstance(data["requests"], list) or not data["requests"]:
            return request.make_json_response(
                {"error": "requests phải là danh sách không rỗng."},
                status=400,
            )

        try:
            deadline = fields.Date.to_date(data["date_deadline"])
        except (TypeError, ValueError):
            return request.make_json_response(
                {"error": "date_deadline không hợp lệ (định dạng chuẩn YYYY-MM-DD)."},
                status=400,
            )

        Partner = request.env["res.partner"].sudo()
        Product = request.env["product.template"].sudo()

        partner = Partner.search(
            [("name", "=", str(data["customer"]).strip())],
            limit=2,
        )

        if len(partner) != 1:
            return request.make_json_response(
                {"error": f"Không tìm thấy duy nhất khách hàng '{data['customer']}'."},
                status=400,
            )

        request_values = []

        for index, item in enumerate(data["requests"]):
            if not isinstance(item, dict):
                return request.make_json_response(
                    {"error": "Mỗi phần tử requests phải là object."},
                    status=400,
                )

            product_name = item.get("product")
            qty = item.get("qty")
            request_date = item.get("date")

            if not product_name or qty is None or not request_date:
                return request.make_json_response(
                    {
                        "error": "Mỗi nhu cầu cần product, qty và date.",
                        "index": index,
                    },
                    status=400,
                )

            try:
                qty = float(qty)
                request_date = fields.Date.to_date(request_date)
            except (TypeError, ValueError):
                return request.make_json_response(
                    {
                        "error": "Số lượng hoặc ngày không hợp lệ.",
                        "index": index,
                    },
                    status=400,
                )

            if qty <= 0:
                return request.make_json_response(
                    {
                        "error": "Số lượng phải lớn hơn 0.",
                        "index": index,
                    },
                    status=400,
                )

            product = Product.search(
                [("name", "=", str(product_name).strip())],
                limit=2,
            )

            if len(product) != 1:
                return request.make_json_response(
                    {
                        "error": f"Không tìm thấy duy nhất sản phẩm '{product_name}'.",
                        "index": index,
                    },
                    status=400,
                )

            request_values.append({
                "product_id": product.id,
                "qty": qty,
                "date": request_date,
                "description": item.get("description", ""),
            })

        # Tạo Cơ hội
        lead = request.env["crm.lead"].sudo().create({
            "name": data["name"],
            "partner_id": partner.id,
            "type": "opportunity",
            "date_deadline": deadline,
            "email_from": data.get("email_from") or data.get("email"),
            "phone": data.get("phone"),
            "description": data.get("description"),
        })

        # Gán ID Cơ hội cho danh sách nhu cầu
        for values in request_values:
            values["opportunity_id"] = lead.id

        # Tạo các dòng nhu cầu khách hàng
        request.env["crm.customer.request"].sudo().create(request_values)

        return request.make_json_response(
            {
                "success": True,
                "message": "Tạo Lead thành công qua API!",
                "lead_id": lead.id,
                "lead_name": lead.name,
                "request_count": len(request_values),
            },
            status=201,
        )