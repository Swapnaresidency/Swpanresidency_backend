from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO

TWOPLACES = Decimal("0.01")


def _half_tax(tax_amount):
    total = Decimal(tax_amount or 0)
    sgst = (total / 2).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    cgst = (total - sgst).quantize(TWOPLACES)
    return sgst, cgst

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from account.models import Institution


def _printed_by(user):
    full_name = (user.get_full_name() or "").strip()
    return full_name or getattr(user, "username", "System")


def _institution():
    return Institution.objects.filter(active=True).first()


def serialize_checkout_rows(checkouts):
    ordered = sorted(
        list(checkouts),
        key=lambda checkout: (
            checkout.checkout_date or datetime.min.date(),
            checkout.id or 0,
        ),
    )
    rows = []
    for checkout in ordered:
        checkin = checkout.checkin
        customer = checkin.customer
        room = checkin.room
        total_amount = Decimal(checkin.total_amount or 0)
        gst_amount = Decimal(checkout.tax or 0)
        sgst, cgst = _half_tax(gst_amount)
        rows.append(
            {
                "receipt_no": f"REC-{checkout.id:06d}",
                "room_no": room.room_no if room else "",
                "guest_name": customer.customer_name if customer else "",
                "gstno": getattr(customer, "gst", None) or "",
                "checkout_date": checkout.checkout_date.strftime("%d-%m-%Y")
                if checkout.checkout_date
                else "",
                "checkout_time": checkout.checkout_time.strftime("%H:%M")
                if checkout.checkout_time
                else "",
                "total_days": checkout.total_days or 0,
                "total_amount": total_amount,
                "sgst": sgst,
                "cgst": cgst,
                "grand_total": total_amount + gst_amount,
                "pay_mode": checkout.pay_mode or "",
                "remarks": checkout.remarks or "",
            }
        )
    return rows


def _header_footer(canvas, doc, institution, printed_by, report_title, period_label):
    canvas.saveState()
    page_width, page_height = landscape(A4)

    y = page_height - 8 * mm
    if institution and getattr(institution, "logo", None):
        try:
            img = ImageReader(institution.logo.path)
            img_w, img_h = img.getSize()
            max_h = 16 * mm
            max_w = 24 * mm
            scale = min(max_w / float(img_w), max_h / float(img_h))
            draw_w = img_w * scale
            draw_h = img_h * scale
            canvas.drawImage(
                img,
                (page_width - draw_w) / 2,
                y - draw_h,
                width=draw_w,
                height=draw_h,
                mask="auto",
            )
            y = y - draw_h - 3 * mm
        except Exception:
            pass

    if institution:
        canvas.setFillColor(colors.HexColor("#1A365D"))
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawCentredString(page_width / 2, y, institution.name or "")
        y -= 5 * mm
        canvas.setFillColor(colors.HexColor("#2D3748"))
        canvas.setFont("Helvetica", 8)
        if institution.address:
            canvas.drawCentredString(page_width / 2, y, str(institution.address).replace("\n", ", "))
            y -= 4 * mm
        contact_parts = []
        if getattr(institution, "mobile", None):
            contact_parts.append(f"Ph: {institution.mobile}")
        if getattr(institution, "email", None):
            contact_parts.append(f"Email: {institution.email}")
        if getattr(institution, "gstin", None):
            contact_parts.append(f"GSTIN: {institution.gstin}")
        if contact_parts:
            canvas.drawCentredString(page_width / 2, y, "  |  ".join(contact_parts))
            y -= 4 * mm

    canvas.setStrokeColor(colors.HexColor("#CBD5E0"))
    canvas.setLineWidth(0.6)
    canvas.line(12 * mm, y - 1 * mm, page_width - 12 * mm, y - 1 * mm)

    footer_y = 10 * mm
    canvas.line(12 * mm, footer_y + 5 * mm, page_width - 12 * mm, footer_y + 5 * mm)
    canvas.setFillColor(colors.HexColor("#4A5568"))
    canvas.setFont("Helvetica", 8)
    printed_at = datetime.now().strftime("%d-%m-%Y %H:%M")
    canvas.drawString(12 * mm, footer_y, f"Printed by: {printed_by}")
    canvas.drawCentredString(page_width / 2, footer_y, f"Page {doc.page}")
    canvas.drawRightString(page_width - 12 * mm, footer_y, f"Printed date: {printed_at}")
    canvas.restoreState()


def build_checkout_report_pdf(checkouts, report_title, period_label, user):
    rows = serialize_checkout_rows(checkouts)
    institution = _institution()
    printed_by = _printed_by(user)

    buffer = BytesIO()
    page_width, page_height = landscape(A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=48 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    cell = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8, leading=10)
    cell_right = ParagraphStyle("CellRight", parent=cell, alignment=2)
    header_cell = ParagraphStyle(
        "HeaderCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1A365D"),
    )
    title_style = ParagraphStyle(
        "SalesTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=10,
    )

    story = [Paragraph(report_title, title_style), Spacer(1, 4)]

    usable_width = page_width - 24 * mm
    col_widths = [
        usable_width * 0.06,
        usable_width * 0.10,
        usable_width * 0.12,
        usable_width * 0.16,
        usable_width * 0.12,
        usable_width * 0.11,
        usable_width * 0.09,
        usable_width * 0.09,
        usable_width * 0.08,
        usable_width * 0.07,
    ]

    table_data = [
        [
            Paragraph("S.No", header_cell),
            Paragraph("Date", header_cell),
            Paragraph("Receipt No", header_cell),
            Paragraph("Guest Name", header_cell),
            Paragraph("gstno", header_cell),
            Paragraph("Total Amount", header_cell),
            Paragraph("SGST (5%)", header_cell),
            Paragraph("CGST (5%)", header_cell),
            Paragraph("Grand Total", header_cell),
            Paragraph("Pay Mode", header_cell),
        ]
    ]

    total_amount_sum = Decimal("0")
    sgst_sum = Decimal("0")
    cgst_sum = Decimal("0")
    grand_sum = Decimal("0")

    for index, row in enumerate(rows, start=1):
        total_amount_sum += row["total_amount"]
        sgst_sum += row["sgst"]
        cgst_sum += row["cgst"]
        grand_sum += row["grand_total"]
        table_data.append(
            [
                Paragraph(str(index), cell),
                Paragraph(str(row["checkout_date"]), cell),
                Paragraph(str(row["receipt_no"]), cell),
                Paragraph(str(row["guest_name"]), cell),
                Paragraph(str(row["gstno"] or "-"), cell),
                Paragraph(f"{row['total_amount']:.2f}", cell_right),
                Paragraph(f"{row['sgst']:.2f}", cell_right),
                Paragraph(f"{row['cgst']:.2f}", cell_right),
                Paragraph(f"{row['grand_total']:.2f}", cell_right),
                Paragraph(str(row["pay_mode"]), cell),
            ]
        )

    table_data.append(
        [
            Paragraph("", cell),
            Paragraph("", cell),
            Paragraph("", cell),
            Paragraph("<b>TOTAL</b>", cell),
            Paragraph("", cell),
            Paragraph(f"<b>{total_amount_sum:.2f}</b>", cell_right),
            Paragraph(f"<b>{sgst_sum:.2f}</b>", cell_right),
            Paragraph(f"<b>{cgst_sum:.2f}</b>", cell_right),
            Paragraph(f"<b>{grand_sum:.2f}</b>", cell_right),
            Paragraph("", cell),
        ]
    )

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    last_row = len(table_data) - 1
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                ("BACKGROUND", (0, last_row), (-1, last_row), colors.HexColor("#E2E8F0")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)

    def on_page(canvas, doc):
        _header_footer(canvas, doc, institution, printed_by, report_title, period_label)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    pdf = buffer.getvalue()
    buffer.close()

    filename = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in report_title).strip()
    filename = f"{filename or 'Checkout_Report'}.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def build_checkout_report_excel(checkouts, report_title, period_label, user):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    rows = serialize_checkout_rows(checkouts)
    institution = _institution()
    printed_by = _printed_by(user)
    printed_at = datetime.now().strftime("%d-%m-%Y %H:%M")

    wb = Workbook()
    ws = wb.active
    ws.title = "Checkout Report"

    last_col = "J"
    headers = [
        "S.No",
        "Date",
        "Receipt No",
        "Guest Name",
        "gstno",
        "Total Amount",
        "SGST (5%)",
        "CGST (5%)",
        "Grand Total",
        "Pay Mode",
    ]

    header_fill = PatternFill("solid", fgColor="1A365D")
    header_font = Font(bold=True, color="FFFFFF")
    total_fill = PatternFill("solid", fgColor="E2E8F0")
    thin = Border(
        left=Side(style="thin", color="CBD5E0"),
        right=Side(style="thin", color="CBD5E0"),
        top=Side(style="thin", color="CBD5E0"),
        bottom=Side(style="thin", color="CBD5E0"),
    )

    ws.merge_cells(f"A1:{last_col}1")
    ws["A1"] = institution.name if institution else report_title
    ws["A1"].font = Font(bold=True, size=14, color="1A365D")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells(f"A2:{last_col}2")
    address = ""
    if institution and institution.address:
        address = str(institution.address).replace("\n", ", ")
    ws["A2"] = address
    ws["A2"].alignment = Alignment(horizontal="center")

    contact_parts = []
    if institution:
        if getattr(institution, "mobile", None):
            contact_parts.append(f"Ph: {institution.mobile}")
        if getattr(institution, "email", None):
            contact_parts.append(f"Email: {institution.email}")
        if getattr(institution, "gstin", None):
            contact_parts.append(f"GSTIN: {institution.gstin}")
    ws.merge_cells(f"A3:{last_col}3")
    ws["A3"] = "  |  ".join(contact_parts)
    ws["A3"].alignment = Alignment(horizontal="center")

    ws.merge_cells(f"A4:{last_col}4")
    ws["A4"] = report_title
    ws["A4"].font = Font(bold=True, size=12, color="1A365D")
    ws["A4"].alignment = Alignment(horizontal="center")

    header_row = 6
    for col, title in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin

    total_amount_sum = Decimal("0")
    sgst_sum = Decimal("0")
    cgst_sum = Decimal("0")
    grand_sum = Decimal("0")
    amount_cols = (6, 7, 8, 9)

    for index, row in enumerate(rows, start=1):
        excel_row = header_row + index
        values = [
            index,
            row["checkout_date"],
            row["receipt_no"],
            row["guest_name"],
            row["gstno"] or "-",
            float(row["total_amount"]),
            float(row["sgst"]),
            float(row["cgst"]),
            float(row["grand_total"]),
            row["pay_mode"],
        ]
        total_amount_sum += row["total_amount"]
        sgst_sum += row["sgst"]
        cgst_sum += row["cgst"]
        grand_sum += row["grand_total"]
        for col, value in enumerate(values, start=1):
            cell = ws.cell(row=excel_row, column=col, value=value)
            cell.border = thin
            if col in amount_cols:
                cell.number_format = "0.00"
                cell.alignment = Alignment(horizontal="right")

    total_row = header_row + len(rows) + 1
    ws.cell(row=total_row, column=4, value="TOTAL").font = Font(bold=True)
    totals = {
        6: total_amount_sum,
        7: sgst_sum,
        8: cgst_sum,
        9: grand_sum,
    }
    for col in range(1, 11):
        cell = ws.cell(row=total_row, column=col)
        cell.border = thin
        cell.fill = total_fill
        if col in totals:
            cell.value = float(totals[col])
            cell.font = Font(bold=True)
            cell.number_format = "0.00"

    footer_row = total_row + 2
    ws.merge_cells(start_row=footer_row, start_column=1, end_row=footer_row, end_column=5)
    ws.cell(row=footer_row, column=1, value=f"Printed by: {printed_by}")
    ws.merge_cells(start_row=footer_row, start_column=7, end_row=footer_row, end_column=10)
    ws.cell(row=footer_row, column=7, value=f"Printed date: {printed_at}")

    widths = [8, 14, 16, 22, 16, 14, 12, 12, 14, 12]
    for i, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in report_title).strip()
    filename = f"{filename or 'Checkout_Report'}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
