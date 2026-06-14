from app.models.quote import Quote


_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 12px; color: #333; }}
    h1 {{ color: #1a56db; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th {{ background: #1a56db; color: white; padding: 8px; text-align: left; }}
    td {{ padding: 6px 8px; border-bottom: 1px solid #e5e7eb; }}
    .totals {{ margin-top: 1rem; text-align: right; }}
    .totals td {{ border: none; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Cotización {quote_number}</h1>
  <p><strong>Estado:</strong> {status} &nbsp; <strong>Moneda:</strong> {currency} &nbsp; <strong>Válida hasta:</strong> {valid_until}</p>
  <table>
    <thead>
      <tr><th>Descripción</th><th>Cant.</th><th>Precio unit.</th><th>Total línea</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  <table class="totals">
    <tr><td>Subtotal</td><td>{currency} {subtotal:.2f}</td></tr>
    <tr><td>IVA ({tax_rate}%)</td><td>{currency} {tax_amount:.2f}</td></tr>
    <tr><td>TOTAL</td><td>{currency} {total:.2f}</td></tr>
  </table>
  {notes_section}
</body>
</html>
"""


def render_quote_html(quote: Quote) -> str:
    rows = "".join(
        f"<tr><td>{item.description}</td><td>{item.quantity}</td>"
        f"<td>{float(item.unit_price):.2f}</td><td>{float(item.line_total):.2f}</td></tr>"
        for item in quote.items
    )
    tax_rate = float(quote.tax_rate)
    subtotal = float(quote.subtotal)
    total = float(quote.total)
    notes_section = f"<p><strong>Notas:</strong> {quote.notes}</p>" if quote.notes else ""

    return _HTML_TEMPLATE.format(
        quote_number=quote.quote_number or "",
        status=quote.status,
        currency=quote.currency,
        valid_until=quote.valid_until or "—",
        rows=rows,
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=total - subtotal,
        total=total,
        notes_section=notes_section,
    )


def generate_pdf_bytes(quote: Quote) -> bytes:
    from weasyprint import HTML
    html = render_quote_html(quote)
    return HTML(string=html).write_pdf()
