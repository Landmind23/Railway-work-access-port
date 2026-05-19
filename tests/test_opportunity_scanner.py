import csv
import tempfile
import unittest
from pathlib import Path

from opportunity_scanner import Opportunity, OpportunityScanner, write_csv


class OpportunityScannerTests(unittest.TestCase):
    def test_extract_from_html_populates_required_fields(self):
        html = """
        <html><body>
            Contact us: tenders@railafrica.org, +27 11 123 4567
            <a href="/tenders/1">Open tender for African railway signaling project (12 months) with Kenya Railways</a>
            <a href="/news/1">General transport bulletin</a>
        </body></html>
        """
        scanner = OpportunityScanner()

        opportunities = scanner._extract_from_html(
            html,
            entity="Rail Africa Agency",
            website="https://railafrica.org",
            page_url="https://railafrica.org/opportunities",
        )

        self.assertEqual(len(opportunities), 1)
        opportunity = opportunities[0]
        self.assertEqual(opportunity.publishing_entity, "Rail Africa Agency")
        self.assertEqual(opportunity.website, "https://railafrica.org")
        self.assertEqual(opportunity.link, "https://railafrica.org/tenders/1")
        self.assertIn("tenders@railafrica.org", opportunity.email)
        self.assertIn("+27 11 123 4567", opportunity.contact_numbers)
        self.assertEqual(opportunity.duration, "12 months")
        self.assertEqual(opportunity.currently_open, "Yes")

    def test_extract_from_rss_filters_relevant_entries(self):
        rss = """
        <rss><channel>
            <item>
                <title>Railway procurement in East Africa now open</title>
                <link>https://example.com/a</link>
                <description>Submit before deadline with Ministry of Transport</description>
            </item>
            <item>
                <title>Unrelated aviation item</title>
                <link>https://example.com/b</link>
                <description>No rail content</description>
            </item>
        </channel></rss>
        """
        scanner = OpportunityScanner()

        opportunities = scanner._extract_from_rss(rss, "Publisher", "https://example.com")

        self.assertEqual(len(opportunities), 1)
        self.assertEqual(opportunities[0].link, "https://example.com/a")
        self.assertEqual(opportunities[0].currently_open, "Yes")

    def test_write_csv_uses_expected_columns(self):
        opportunities = [
            Opportunity(
                publishing_entity="Entity",
                website="https://entity.example",
                link="https://entity.example/opportunity",
                contact_numbers="+254700000000",
                email="info@entity.example",
                project_name="African Rail Upgrade",
                duration="24 months",
                currently_open="No",
                key_players="Entity",
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "sheet.csv"
            write_csv(opportunities, output_path)
            with output_path.open("r", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["project_name"], "African Rail Upgrade")
        self.assertIn("currently_open", rows[0])


if __name__ == "__main__":
    unittest.main()
