#!/usr/bin/env python3
"""
CourtListener Citation Lookup Script for Feynman Legal Skills

Sends text to the CourtListener Citation Lookup API (v4) to extract
and verify legal citations against their database of ~10M opinions.

Usage:
    python3 courtlistener_lookup.py --text "Brown v. Board of Education, 347 U.S. 483 (1954)"
    python3 courtlistener_lookup.py --file brief.txt
    python3 courtlistener_lookup.py --file brief.txt --token YOUR_API_TOKEN

API docs: https://www.courtlistener.com/help/api/rest/citation-lookup/
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

API_URL = "https://www.courtlistener.com/api/rest/v4/citation-lookup/"
MAX_TEXT_LENGTH = 64000
MAX_CITATIONS_PER_REQUEST = 250


def get_api_token():
    """Get API token from env var or config file."""
    token = os.environ.get("COURTLISTENER_API_TOKEN")
    if token:
        return token

    config_path = os.path.expanduser("~/.feynman/courtlistener_token")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return f.read().strip()

    return None


def read_file(filepath):
    """Read text from a file. Supports .txt and .md directly."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def chunk_text(text, max_length=MAX_TEXT_LENGTH):
    """Split text into chunks that fit the API limit."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        # Find a good split point (end of sentence or paragraph)
        split_at = text.rfind("\n\n", 0, max_length)
        if split_at == -1:
            split_at = text.rfind(". ", 0, max_length)
        if split_at == -1:
            split_at = max_length

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    return chunks


def lookup_citations(text, token=None):
    """Send text to CourtListener Citation Lookup API."""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    data = urllib.parse.urlencode({"text": text}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {str(e)}"}


def process_results(api_response):
    """Parse API response into structured citation results."""
    if "error" in api_response:
        return {
            "status": "error",
            "message": api_response["error"],
            "matched": [],
            "unmatched": [],
            "ambiguous": [],
        }

    matched = []
    unmatched = []
    ambiguous = []

    citations = api_response if isinstance(api_response, list) else api_response.get("citations", [])

    for cite in citations:
        citation_string = cite.get("citation", cite.get("citation_string", ""))
        status = cite.get("status", "")
        normalized = cite.get("normalized_citations", [])

        if status == "matched" or cite.get("clusters"):
            clusters = cite.get("clusters", [])
            for cluster in clusters:
                matched.append({
                    "citation": citation_string,
                    "case_name": cluster.get("case_name", "Unknown"),
                    "court": cluster.get("court", "Unknown"),
                    "year": cluster.get("date_filed", "Unknown")[:4] if cluster.get("date_filed") else "Unknown",
                    "cluster_id": cluster.get("id"),
                    "url": f"https://www.courtlistener.com/opinion/{cluster.get('id')}/",
                    "absolute_url": cluster.get("absolute_url", ""),
                })
            if not clusters:
                matched.append({
                    "citation": citation_string,
                    "case_name": cite.get("case_name", "Unknown"),
                    "court": cite.get("court", "Unknown"),
                    "year": "Unknown",
                    "cluster_id": None,
                    "url": "",
                })
        elif status == "ambiguous" or len(normalized) > 1:
            ambiguous.append({
                "citation": citation_string,
                "possible_matches": normalized,
            })
        else:
            unmatched.append({
                "citation": citation_string,
                "raw": cite,
            })

    return {
        "status": "ok",
        "total": len(citations),
        "matched": matched,
        "unmatched": unmatched,
        "ambiguous": ambiguous,
        "summary": {
            "total": len(citations),
            "matched": len(matched),
            "unmatched": len(unmatched),
            "ambiguous": len(ambiguous),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Verify legal citations via CourtListener API"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text containing legal citations")
    group.add_argument("--file", help="Path to file containing legal citations")
    parser.add_argument("--token", help="CourtListener API token (or set COURTLISTENER_API_TOKEN)")
    parser.add_argument("--raw", action="store_true", help="Output raw API response")
    args = parser.parse_args()

    token = args.token or get_api_token()

    if args.file:
        text = read_file(args.file)
    else:
        text = args.text

    if not text.strip():
        print(json.dumps({"error": "No text provided"}))
        sys.exit(1)

    chunks = chunk_text(text)
    all_results = {
        "status": "ok",
        "matched": [],
        "unmatched": [],
        "ambiguous": [],
    }

    for i, chunk in enumerate(chunks):
        if i > 0:
            # Rate limiting: 60 citations/minute
            time.sleep(1)

        result = lookup_citations(chunk, token)

        if args.raw:
            print(json.dumps(result, indent=2))
            continue

        processed = process_results(result)

        if processed["status"] == "error":
            print(json.dumps(processed, indent=2))
            sys.exit(1)

        all_results["matched"].extend(processed["matched"])
        all_results["unmatched"].extend(processed["unmatched"])
        all_results["ambiguous"].extend(processed["ambiguous"])

    if not args.raw:
        all_results["summary"] = {
            "total_chunks": len(chunks),
            "total_matched": len(all_results["matched"]),
            "total_unmatched": len(all_results["unmatched"]),
            "total_ambiguous": len(all_results["ambiguous"]),
        }
        print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    main()
