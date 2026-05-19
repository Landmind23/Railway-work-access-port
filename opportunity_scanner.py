#!/usr/bin/env python3
"""Collect railway opportunities in Africa and export them to CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urljoin, urlparse

RAIL_KEYWORDS = ("rail", "railway", "metro", "tram", "perway")
AFRICA_KEYWORDS = ("africa", "african")
OPPORTUNITY_KEYWORDS = (
    "tender",
    "opportunity",
    "procurement",
    "bid",
    "eoi",
    "rfp",
    "project",
)

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MIN_PHONE_DIGITS = 7
MAX_PLAYER_NAME_LENGTH = 40
PHONE_PATTERN = re.compile(r"(?:\+\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?){2,4}\d{2,4}")
DURATION_PATTERN = re.compile(r"\b\d+\s*(?:day|week|month|year)s?\b", re.IGNORECASE)


@dataclass
class Opportunity:
    publishing_entity: str
    website: str
    link: str
    contact_numbers: str
    email: str
    project_name: str
    duration: str
    currently_open: str
    key_players: str


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[tuple[str, str]] = []
        self._active_link: str | None = None
        self._active_text: List[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._active_link = href
            self._active_text = []

    def handle_data(self, data: str) -> None:
        if self._active_link is not None and data.strip():
            self._active_text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._active_link:
            text = " ".join(self._active_text).strip()
            self.links.append((self._active_link, text))
            self._active_link = None
            self._active_text = []


class OpportunityScanner:
    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def fetch_url(self, url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "RailwayOpportunityScanner/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return response.read().decode("utf-8", errors="replace")

    def scan(self, sources: list[dict[str, str]]) -> list[Opportunity]:
        opportunities: list[Opportunity] = []
        for source in sources:
            entity = source.get("publishing_entity", "Unknown")
            url = source["url"]
            website = source.get("website") or self._website_from_url(url)
            content = self.fetch_url(url)

            if self._looks_like_xml(content):
                opportunities.extend(self._extract_from_rss(content, entity, website))
            else:
                opportunities.extend(self._extract_from_html(content, entity, website, url))

        return self._deduplicate(opportunities)

    def _extract_from_html(self, html: str, entity: str, website: str, page_url: str) -> list[Opportunity]:
        parser = LinkParser()
        parser.feed(html)

        contacts = self._extract_contacts(html)
        opportunities: list[Opportunity] = []
        for href, text in parser.links:
            combined = f"{text} {href}".lower()
            if not self._is_relevant(combined):
                continue

            resolved_link = urljoin(page_url, href)
            opportunities.append(
                Opportunity(
                    publishing_entity=entity,
                    website=website,
                    link=resolved_link,
                    contact_numbers=contacts["phones"],
                    email=contacts["emails"],
                    project_name=text or "Untitled railway opportunity",
                    duration=self._extract_duration(text),
                    currently_open=self._infer_open_status(text),
                    key_players=self._extract_key_players(text, entity),
                )
            )

        return opportunities

    def _extract_from_rss(self, xml_text: str, entity: str, website: str) -> list[Opportunity]:
        root = ET.fromstring(xml_text)
        opportunities: list[Opportunity] = []
        for item in root.findall(".//item") + root.findall(".//entry"):
            title = self._node_text(item, "title")
            link = self._rss_link(item)
            description = self._node_text(item, "description") + " " + self._node_text(item, "summary")
            combined = f"{title} {description} {link}".lower()
            if not self._is_relevant(combined):
                continue

            opportunities.append(
                Opportunity(
                    publishing_entity=entity,
                    website=website,
                    link=link,
                    contact_numbers="",
                    email="",
                    project_name=title or "Untitled railway opportunity",
                    duration=self._extract_duration(description),
                    currently_open=self._infer_open_status(description),
                    key_players=self._extract_key_players(description, entity),
                )
            )

        return opportunities

    @staticmethod
    def _node_text(node: ET.Element, tag_name: str) -> str:
        for child in node.iter():
            if child.tag.split("}")[-1] == tag_name and child.text:
                return child.text.strip()
        return ""

    @staticmethod
    def _rss_link(node: ET.Element) -> str:
        for child in node.iter():
            if child.tag.split("}")[-1] == "link":
                if child.text and child.text.strip():
                    return child.text.strip()
                href = child.attrib.get("href")
                if href:
                    return href.strip()
        return ""

    @staticmethod
    def _website_from_url(url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else url

    @staticmethod
    def _looks_like_xml(text: str) -> bool:
        trimmed = text.lstrip()
        return trimmed.startswith("<?xml") or trimmed.startswith("<rss") or trimmed.startswith("<feed")

    @staticmethod
    def _extract_contacts(text: str) -> dict[str, str]:
        emails = sorted(set(EMAIL_PATTERN.findall(text)))
        phone_matches = PHONE_PATTERN.findall(text)
        phones = sorted(
            set(phone.strip() for phone in phone_matches if len(re.sub(r"\D", "", phone)) >= MIN_PHONE_DIGITS)
        )
        return {"emails": "; ".join(emails), "phones": "; ".join(phones)}

    @staticmethod
    def _extract_duration(text: str) -> str:
        match = DURATION_PATTERN.search(text)
        return match.group(0) if match else ""

    @staticmethod
    def _infer_open_status(text: str) -> str:
        normalized = text.lower()
        if any(word in normalized for word in ("closed", "expired", "awarded")):
            return "No"
        if any(word in normalized for word in ("open", "deadline", "apply", "submit")):
            return "Yes"
        return "Unknown"

    @staticmethod
    def _extract_key_players(text: str, fallback: str) -> str:
        players = re.findall(rf"(?:by|with|from)\s+([A-Z][A-Za-z&\-\s]{2,{MAX_PLAYER_NAME_LENGTH}})", text)
        cleaned = sorted({player.strip(" .,;") for player in players if player.strip()})
        return "; ".join(cleaned) if cleaned else fallback

    @staticmethod
    def _is_relevant(text: str) -> bool:
        has_rail = any(keyword in text for keyword in RAIL_KEYWORDS)
        has_africa = any(keyword in text for keyword in AFRICA_KEYWORDS)
        has_opportunity = any(keyword in text for keyword in OPPORTUNITY_KEYWORDS)
        return has_rail and has_africa and has_opportunity

    @staticmethod
    def _deduplicate(opportunities: Iterable[Opportunity]) -> list[Opportunity]:
        seen_links: set[str] = set()
        unique: list[Opportunity] = []
        for item in opportunities:
            key = item.link.strip()
            if not key or key in seen_links:
                continue
            seen_links.add(key)
            unique.append(item)
        return unique


def load_sources(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("sources file must be a JSON array")
    sources: list[dict[str, str]] = []
    for entry in data:
        if not isinstance(entry, dict) or "url" not in entry:
            raise ValueError("each source must be an object containing at least a 'url'")
        sources.append({k: str(v) for k, v in entry.items()})
    return sources


def write_csv(opportunities: list[Opportunity], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "publishing_entity",
        "website",
        "link",
        "contact_numbers",
        "email",
        "project_name",
        "duration",
        "currently_open",
        "key_players",
    ]
    with output_file.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for item in opportunities:
            writer.writerow(asdict(item))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan railway opportunities in Africa and export to CSV")
    parser.add_argument("--sources", default="sources.json", help="JSON file with source websites/feed URLs")
    parser.add_argument("--output", default="output/railway_opportunities.csv", help="CSV output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scanner = OpportunityScanner()
    sources = load_sources(Path(args.sources))
    opportunities = scanner.scan(sources)
    write_csv(opportunities, Path(args.output))
    print(f"Exported {len(opportunities)} opportunities to {args.output}")


if __name__ == "__main__":
    main()
