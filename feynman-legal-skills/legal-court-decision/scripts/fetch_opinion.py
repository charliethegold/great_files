#!/usr/bin/env python3
"""
Fetch a court opinion from CourtListener by URL, cluster ID, or citation.

Usage:
    python3 fetch_opinion.py --url https://www.courtlistener.com/opinion/12345/case-name/
    python3 fetch_opinion.py --cluster-id 12345
    python3 fetch_opinion.py --citation "347 U.S. 483"
    python3 fetch_opinion.py --search "Brown v. Board of Education"

API docs: https://www.courtlistener.com/help/api/rest/case-law/
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "https://www.courtlistener.com/api/rest/v4"


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


def api_get(url, token=None):
    """Make a GET request to the CourtListener API."""
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Token {token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {str(e)}"}


def extract_cluster_id_from_url(url):
    """Extract cluster ID from a CourtListener opinion URL."""
    match = re.search(r"/opinion/(\d+)/", url)
    if match:
        return int(match.group(1))
    return None


def lookup_citation(citation_text, token=None):
    """Look up a citation string to find its cluster ID."""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    url = f"{BASE_URL}/citation-lookup/"
    data = urllib.parse.urlencode({"text": citation_text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            citations = result if isinstance(result, list) else result.get("citations", [])
            for cite in citations:
                clusters = cite.get("clusters", [])
                if clusters:
                    return clusters[0]
            return None
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"Error looking up citation: {e}", file=sys.stderr)
        return None


def search_cases(query, token=None):
    """Search for cases by name or keywords."""
    params = urllib.parse.urlencode({"q": query, "type": "o"})
    url = f"{BASE_URL}/search/?{params}"
    return api_get(url, token)


def fetch_cluster(cluster_id, token=None):
    """Fetch cluster (case) metadata."""
    url = f"{BASE_URL}/clusters/{cluster_id}/"
    return api_get(url, token)


def fetch_opinions(cluster_id, token=None):
    """Fetch all opinions for a cluster."""
    url = f"{BASE_URL}/opinions/?cluster={cluster_id}"
    return api_get(url, token)


def fetch_full_opinion(cluster_id, token=None):
    """Fetch complete opinion data: metadata + text."""
    cluster = fetch_cluster(cluster_id, token)
    if "error" in cluster:
        return cluster

    opinions = fetch_opinions(cluster_id, token)
    if "error" in opinions:
        opinions = {"results": []}

    opinion_texts = []
    for op in opinions.get("results", []):
        text = (
            op.get("plain_text")
            or op.get("html_with_citations")
            or op.get("html")
            or op.get("html_columbia")
            or op.get("html_lawbox")
            or ""
        )
        # Strip HTML tags for plain text output
        if text.startswith("<"):
            text = re.sub(r"<[^>]+>", "", text)
            text = re.sub(r"\s+", " ", text).strip()

        opinion_texts.append({
            "type": op.get("type", "unknown"),
            "author": op.get("author_str", ""),
            "text": text,
            "word_count": len(text.split()),
        })

    return {
        "case_name": cluster.get("case_name", "Unknown"),
        "case_name_full": cluster.get("case_name_full", ""),
        "court": cluster.get("court", ""),
        "court_id": cluster.get("court_id", ""),
        "date_filed": cluster.get("date_filed", "Unknown"),
        "docket_number": cluster.get("docket_number", ""),
        "citations": cluster.get("citations", []),
        "judges": cluster.get("judges", ""),
        "precedential_status": cluster.get("precedential_status", "Unknown"),
        "cluster_id": cluster_id,
        "url": f"https://www.courtlistener.com/opinion/{cluster_id}/",
        "opinions": opinion_texts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch court opinions from CourtListener"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="CourtListener opinion URL")
    group.add_argument("--cluster-id", type=int, help="CourtListener cluster ID")
    group.add_argument("--citation", help="Citation string (e.g., '347 U.S. 483')")
    group.add_argument("--search", help="Search for a case by name")
    parser.add_argument("--token", help="CourtListener API token")
    parser.add_argument("--text-only", action="store_true", help="Output only the opinion text")
    parser.add_argument("--output", help="Save output to file")
    args = parser.parse_args()

    token = args.token or get_api_token()

    if args.url:
        cluster_id = extract_cluster_id_from_url(args.url)
        if not cluster_id:
            print(json.dumps({"error": f"Could not extract cluster ID from URL: {args.url}"}))
            sys.exit(1)
    elif args.citation:
        result = lookup_citation(args.citation, token)
        if not result:
            print(json.dumps({"error": f"Citation not found: {args.citation}"}))
            sys.exit(1)
        cluster_id = result.get("id")
        if not cluster_id:
            print(json.dumps({"error": "No cluster ID in citation lookup result", "data": result}))
            sys.exit(1)
    elif args.search:
        results = search_cases(args.search, token)
        if "error" in results:
            print(json.dumps(results, indent=2))
            sys.exit(1)
        search_results = results.get("results", [])
        if not search_results:
            print(json.dumps({"error": f"No cases found for: {args.search}"}))
            sys.exit(1)
        # Show top results and use the first
        print(f"Found {len(search_results)} results. Using first match.", file=sys.stderr)
        cluster_id = search_results[0].get("cluster_id")
        if not cluster_id:
            print(json.dumps({"error": "No cluster ID in search result", "data": search_results[0]}))
            sys.exit(1)
    else:
        cluster_id = args.cluster_id

    opinion = fetch_full_opinion(cluster_id, token)

    if args.text_only:
        for op in opinion.get("opinions", []):
            if op.get("text"):
                output = op["text"]
                break
        else:
            output = "No opinion text available."

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Opinion text saved to {args.output}", file=sys.stderr)
        else:
            print(output)
    else:
        output = json.dumps(opinion, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Opinion data saved to {args.output}", file=sys.stderr)
        else:
            print(output)


if __name__ == "__main__":
    main()
