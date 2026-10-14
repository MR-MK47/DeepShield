"""Discover public contact email addresses from a result website's own pages.

Only same-host public HTTP(S) pages are considered. Redirects are followed only
to the same host or its www/non-www equivalent; private/reserved IPs are blocked.
Discovery is a hint, not verification that an address is the correct legal contact.
"""
from __future__ import annotations

import ipaddress
import logging
import re
import socket
from html import unescape
from urllib.parse import urljoin, urlparse

import requests

logger = logging.getLogger(__name__)
MAX_HTML_BYTES = 750_000
MAX_PAGES = 7
EMAIL_RE = re.compile(
    r"(?<![A-Z0-9._%+-])[A-Z0-9._%+-]{1,64}@[A-Z0-9.-]{1,190}\.[A-Z]{2,24}(?![A-Z0-9.-])",
    re.IGNORECASE,
)
CONTACT_PATHS = (
    "/", "/contact", "/contact-us", "/contactus", "/about/contact",
    "/privacy-policy", "/terms", "/terms-of-service", "/terms-and-conditions",
)


def _host_variants(host: str) -> set[str]:
    host = host.lower().rstrip(".")
    if host.startswith("www."):
        return {host, host[4:]}
    return {host, "www." + host}


def _is_public_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    if parsed.username or parsed.password or parsed.port not in {None, 80, 443}:
        return False
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".test", ".invalid")):
        return False
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            addresses = [
                ipaddress.ip_address(item[4][0])
                for item in socket.getaddrinfo(
                    host, 443 if parsed.scheme == "https" else 80, type=socket.SOCK_STREAM
                )
            ]
        except (OSError, ValueError):
            return False
    return bool(addresses) and all(address.is_global for address in addresses)


def _fetch_html(url: str, allowed_hosts: set[str]) -> tuple[str, str] | None:
    current_url = url
    for _ in range(3):
        if not _is_public_url(current_url):
            return None
        parsed = urlparse(current_url)
        if (parsed.hostname or "").lower().rstrip(".") not in allowed_hosts:
            return None
        try:
            with requests.get(
                current_url,
                timeout=(2.5, 4.0),
                stream=True,
                allow_redirects=False,
                headers={"User-Agent": "DeepShield contact discovery (+public website contact page)"},
            ) as response:
                if response.is_redirect or response.is_permanent_redirect:
                    location = response.headers.get("location")
                    if not location:
                        return None
                    next_url = urljoin(current_url, location)
                    next_host = (urlparse(next_url).hostname or "").lower().rstrip(".")
                    if next_host not in allowed_hosts or not _is_public_url(next_url):
                        return None
                    current_url = next_url
                    continue
                if response.status_code != 200:
                    return None
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    return None
                body = bytearray()
                for chunk in response.iter_content(chunk_size=16 * 1024):
                    if not chunk:
                        continue
                    body.extend(chunk)
                    if len(body) > MAX_HTML_BYTES:
                        break
                encoding = response.encoding or "utf-8"
                return bytes(body[:MAX_HTML_BYTES]).decode(encoding, errors="replace"), current_url
        except requests.RequestException as exc:
            logger.debug("Contact discovery request failed for %s: %s", current_url, exc)
            return None
    return None


def _rank_email(email: str) -> tuple[int, str]:
    local = email.split("@", 1)[0].lower().replace(".", "").replace("-", "")
    if any(term in local for term in ("dmca", "copyright", "legal", "abuse", "grievance")):
        score = 0
    elif "privacy" in local or "dataprotection" in local:
        score = 1
    elif any(term in local for term in ("support", "contact", "info", "help")):
        score = 2
    elif "admin" in local or "webmaster" in local:
        score = 3
    elif "sales" in local:
        score = 4
    else:
        score = 5
    return score, email.lower()


def discover_public_contacts(target_url: str) -> dict:
    """Return email candidates visibly published on a result site's public pages."""
    parsed = urlparse(target_url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if not _is_public_url(target_url) or not host:
        return {"domain": host, "contacts": [], "suggested_email": None}

    allowed_hosts = _host_variants(host)
    scheme = parsed.scheme
    base_host = "www." + host[4:] if host.startswith("www.") else host
    candidates: dict[str, dict[str, str]] = {}

    for path in CONTACT_PATHS[:MAX_PAGES]:
        page_url = f"{scheme}://{base_host}{path}"
        fetched = _fetch_html(page_url, allowed_hosts)
        if fetched is None:
            # Also try the actual source host for sites where only www/non-www responds.
            if host != base_host:
                fetched = _fetch_html(f"{scheme}://{host}{path}", allowed_hosts)
            if fetched is None:
                continue
        html, source_url = fetched
        decoded = unescape(html)
        found = {email.strip(".,;:!?()[]{}<>\\"'").lower() for email in EMAIL_RE.findall(decoded)}
        # mailto links may include query parameters; the general expression catches the address,
        # but extracting href gives another chance on HTML-encoded links.
        for match in re.findall(r"""mailto:([^"'?\s>]+)""", decoded, flags=re.IGNORECASE):
            match = unescape(match).strip().lower()
            if EMAIL_RE.fullmatch(match):
                found.add(match)
        for email in found:
            if len(email) <= 254:
                candidates.setdefault(email, {"email": email, "source_url": source_url})

    contacts = sorted(candidates.values(), key=lambda item: _rank_email(item["email"]))
    return {
        "domain": host,
        "contacts": contacts[:12],
        "suggested_email": contacts[0]["email"] if contacts else None,
    }
