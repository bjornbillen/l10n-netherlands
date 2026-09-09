### Contribute payment experience to Liza

![Liza for Odoo](../static/description/banner.png)

**Liza Payment Information** is an extension of **Liza Business Information**
(`liza_base`) and cannot be used on its own. Where the base module *reads*
company data from Liza, this module adds the *sharing* side: it automatically
sends your open customer invoices to Liza's AutoPayex service every day.

Liza aggregates this into a picture of how quickly companies pay their suppliers
— the very payment-experience data you can then consult on enriched contacts in
the base module. The more customers contribute, the sharper that picture becomes
for everyone.

### What this module adds — and does not do

- **Included:** a daily scheduled action that sends your posted, unpaid customer
  invoices (open amount, customer identifier and country) to Liza.
- **Not included:** contact enrichment, financial-health data, the health
  barometer, alerts or any of the viewing features — those all live in **Liza
  Business Information**, which this module requires.

### How it works

- A daily scheduled action collects all posted, unpaid customer invoices.
- Partial payments are supported — only the outstanding amount is reported.
- Credit notes are excluded automatically.
- Only customers in supported countries (NL, BE, LU, FR) with a VAT or
  registration number are submitted.

### What is shared

- Your company: VAT/registration number and country.
- Per invoice: customer VAT/registration number, country, invoice number, date
  and amount due.

### Requirements

Requires **Liza Business Information** (`liza_base`) with valid Liza credentials
configured. Install that module first.
