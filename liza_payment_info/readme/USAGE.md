Configuration
-------------
1. Set up your Liza credentials under Contacts > Liza > Settings.
2. Go to Settings > Liza > Payment Info and enable
   **Send Open Invoices to Liza** for your company (enabled by default).

The scheduled action **Liza: Send Open Invoices** runs once per day and
submits all posted, unpaid customer invoices to Liza. Invoices for
customers without a VAT number or company registry number, or in unsupported
countries, are skipped silently.

The result of each submission is logged as an info message, including the number
of valid and invalid invoices processed and the total open amount reported.
