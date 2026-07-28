# Copyright 2026 Dynapps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Unit tests for the pure Liza helper functions (no API call / cassette needed).

from unittest.mock import patch

from freezegun import freeze_time

from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon

from ..liza_format import (
    format_date,
    format_float_value,
    format_industry,
    format_warnings,
)
from ..liza_utils import (
    _liza_create_hash,
    _liza_get_service_args,
    get_country_code_from_vat,
    get_enable_field,
    liza_client,
)


class TestLizaHelpers(BaseCommon):
    @freeze_time("2026-07-24")
    def test_create_hash_matches_documented_example(self):
        """Reproduce the reference hash from the Liza API guidelines.

        docs.liza.nl: today=20260724, login=MYNAME, password=ABC123,
        secret=BD5899FE-2759-4944-8948-B5D4063C05CB
        -> 6984600a575f1435c2e6bde5adf63ffa12f1a804
        """
        self.assertEqual(
            _liza_create_hash(
                "MYNAME", "ABC123", "BD5899FE-2759-4944-8948-B5D4063C05CB"
            ),
            "6984600a575f1435c2e6bde5adf63ffa12f1a804",
        )

    def test_get_country_code_from_vat(self):
        # Only the allowed uppercase country prefixes are recognised
        self.assertEqual(get_country_code_from_vat("BE0405056855"), "BE")
        self.assertEqual(get_country_code_from_vat("LU26832882"), "LU")
        self.assertEqual(get_country_code_from_vat("NL810433941B01"), "NL")
        self.assertEqual(get_country_code_from_vat("FR76803453802"), "FR")
        # No country prefix / not allowed / empty
        self.assertFalse(get_country_code_from_vat("0405056855"))
        self.assertFalse(get_country_code_from_vat("DE123456789"))
        self.assertFalse(get_country_code_from_vat(""))
        self.assertFalse(get_country_code_from_vat(False))

    def test_get_enable_field(self):
        self.assertEqual(get_enable_field("liza_name"), "liza_name_enable")
        # A trailing '_id' is stripped before adding '_enable'
        self.assertEqual(get_enable_field("liza_prefLang_id"), "liza_prefLang_enable")

    def test_get_service_args_by_vat(self):
        service, args, missing = _liza_get_service_args(vat="BE0405056855")
        self.assertEqual(service, "GetCompanyByVat")
        self.assertEqual(args["VatNumber"], "BE0405056855")
        self.assertEqual(args["CountryCode"], "BE")
        self.assertFalse(missing)

    def test_get_service_args_by_registry(self):
        service, args, missing = _liza_get_service_args(
            registry="0405056855", country_code="BE"
        )
        self.assertEqual(service, "GetCompanyByRegistrationNumber")
        self.assertEqual(args["RegistrationNumber"], "0405056855")
        self.assertEqual(args["CountryCode"], "BE")
        self.assertFalse(missing)

    def test_get_service_args_by_search_prefers_zip_over_city(self):
        service, args, _ = _liza_get_service_args(
            search="ACME", zip="9100", city="Sint-Niklaas", country_code="BE"
        )
        self.assertEqual(service, "SearchCompanies")
        self.assertEqual(args["SearchTerm"], "ACME")
        self.assertEqual(args["PostalCodeOrCityName"], "9100")

    def test_get_service_args_by_search_falls_back_to_city(self):
        _, args, _ = _liza_get_service_args(
            search="ACME", city="Sint-Niklaas", country_code="BE"
        )
        self.assertEqual(args["PostalCodeOrCityName"], "Sint-Niklaas")

    def test_get_service_args_missing_everything(self):
        service, _, missing = _liza_get_service_args()
        self.assertFalse(service)
        self.assertIn("Country", missing)
        self.assertIn("VAT", missing)
        self.assertIn("Company ID", missing)
        self.assertIn("Search Term", missing)

    def test_format_float_value_distinguishes_zero_from_none(self):
        # 0 must stay 0.0 (a disclosed zero), not be turned into None
        self.assertEqual(format_float_value(0), 0.0)
        self.assertEqual(format_float_value("12.5"), 12.5)
        # Undisclosed values collapse to None
        self.assertIsNone(format_float_value(False))
        self.assertIsNone(format_float_value(None))
        self.assertIsNone(format_float_value(""))

    def test_format_date(self):
        self.assertEqual(format_date("20240131").isoformat()[:10], "2024-01-31")
        # Invalid / empty input is returned as False
        self.assertFalse(format_date("not-a-date"))
        self.assertFalse(format_date(False))

    def test_format_industry(self):
        self.assertEqual(
            format_industry({"Code": "23650", "Description": "Fibre cement"}),
            "23650 - Fibre cement",
        )

    def test_format_warnings(self):
        self.assertEqual(
            format_warnings({"string": ["Warning 1", "Warning 2"]}),
            "- Warning 1\n- Warning 2",
        )

    def test_liza_client_sets_recommended_headers(self):
        """liza_client must attach the Api-Client-* headers Liza recommends."""
        with patch("odoo.addons.liza_base.liza_utils.Client") as mock_client:
            liza_client("https://connect.liza.nl/V2.0/alacarteservice.asmx")
        transport = mock_client.call_args.kwargs["transport"]
        headers = transport.session.headers
        self.assertEqual(headers["Api-Client-Name"], "Odoo liza_base")
        # Version comes from the module manifest and must be non-empty
        self.assertTrue(headers["Api-Client-Version"])

    @mute_logger("odoo.addons.liza_base.models.res_partner")
    def test_liza_image_tag(self):
        """The health-barometer HTML tag is built only for existing images."""
        partner = self.env["res.partner"].create({"name": "T", "is_company": True})
        # A barometer image that ships with the module -> an <img> tag
        partner.liza_image = "pos-01.png"
        self.assertIn(
            "liza_base/static/img/liza_barometer/pos-01.png", partner.liza_image_tag
        )
        # A missing file -> no tag (warning branch)
        partner.liza_image = "does-not-exist.png"
        self.assertFalse(partner.liza_image_tag)
        # No image at all -> no tag
        partner.liza_image = False
        self.assertFalse(partner.liza_image_tag)
