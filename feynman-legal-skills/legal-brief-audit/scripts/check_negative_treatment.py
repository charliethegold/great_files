#!/usr/bin/env python3
"""
Check negative treatment of a case via CourtListener's citation graph API.

Given a CourtListener cluster ID (opinion), this script checks what later
opinions cite it and flags any that may indicate negative treatment
(overruled, distinguished, abrogated, questioned).

Usage:
    python3 check_negative_treatment.py --cluster-id 2812209
    python3 check_negative_treatment.py --citation "347 U.S. 483"

API docs: https://www.courtlistener.com/help/api/rest/citations/
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "https://www.courtlistener.com/api/rest/v4"

# Keywords in opinion text that suggest negative treatment
NEGATIVE_SIGNALS = [
    "overruled",
    "overrule",
    "abrogated",
    "abrogate",
    "no longer good law",
    "no longer controlling",
    "superseded",
    "vacated",
    "reversed",
    "disapproved",
    "rejected",
    "questioned",
    "criticized",
    "distinguished",
    "limited",
    "narrowed",
]


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


def api_get(endpoint, token=None, params=None):
    """Make a GET request to the CourtListener API."""
    url = f"{BASE_URL}/{endpoint}/"
    if params:
        url += "?" + urllib.parse.urlencode(params)

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


def get_citing_opinions(cluster_id, token=None):
    """Get opinions that cite the given cluster (forward citations)."""
    result = api_get("opinions-cited", token, {
        "cited_opinion__cluster": cluster_id,
        "page_size": 100,
    })
    return result


def get_cluster_info(cluster_id, token=None):
    """Get basic info about an opinion cluster."""
    return api_get(f"clusters/{cluster_id}", token)


def lookup_citation_to_cluster(citation_text, token=None):
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
                    return clusters[0].get("id")
            return None
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def check_negative_treatment(cluster_id, token=None):
    """Check if a case has received negative treatment."""
    # Get info about the original case
    cluster_info = get_cluster_info(cluster_id, token)
    if "error" in cluster_info:
        return {"error": cluster_info["error"]}

    case_name = cluster_info.get("case_name", "Unknown")
    date_filed = cluster_info.get("date_filed", "Unknown")

    # Get forward citations (opinions that cite this case)
    citing = get_citing_opinions(cluster_id, token)
    if "error" in citing:
        return {
            "case_name": case_name,
            "date_filed": date_filed,
            "cluster_id": cluster_id,
            "error": citing["error"],
            "warning": "Could not retrieve citing opinions",
        }

    results_list = citing.get("results", [])
    total_citing = citing.get("count", len(results_list))

    # Analyze citing opinions for negative treatment signals
    negative_flags = []
    for citing_op in results_list:
        text_snippet = (citing_op.get("plain_text", "") or "")[:2000].lower()
        found_signals = [s for s in NEGATIVE_SIGNALS if s in text_snippet]
        if found_signals:
            negative_flags.append({
                "citing_case": citing_op.get("case_name", "Unknown"),
                "citing_court": citing_op.get("court", "Unknown"),
                "date": citing_op.get("date_filed", "Unknown"),
                "signals_found": found_signals,
                "cluster_id": citing_op.get("cluster_id"),
            })

    treatment = "positive"
    if any("overruled" in f.get("signals_found", []) or "overrule" in f.get("signals_found", []) for f in negative_flags):
        treatment = "overruled"
    elif any("abrogated" in f.get("signals_found", []) or "abrogate" in f.get("signals_found", []) for f in negative_flags):
        treatment = "abrogated"
    elif any("distinguished" in f.get("signals_found", []) for f in negative_flags):
        treatment = "distinguished"
    elif any("questioned" in f.get("signals_found", []) or "criticized" in f.get("signals_found", []) for f in negative_flags):
        treatment = "questioned"
    elif negative_flags:
        treatment = "caution"

    return {
        "case_name": case_name,
        "date_filed": date_filed,
        "cluster_id": cluster_id,
        "url": f"https://www.courtlistener.com/opinion/{cluster_id}/",
        "total_citing_opinions": total_citing,
        "treatment": treatment,
        "negative_flags": negative_flags,
        "flag_count": len(negative_flags),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check negative treatment of a legal case via CourtListener"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cluster-id", type=int, help="CourtListener cluster ID")
    group.add_argument("--citation", help="Citation string to look up (e.g., '347 U.S. 483')")
    parser.add_argument("--token", help="CourtListener API token")
    args = parser.parse_args()

    token = args.token or get_api_token()

    if args.citation:
        cluster_id = lookup_citation_to_cluster(args.citation, token)
        if not cluster_id:
            print(json.dumps({
                "error": f"Could not find cluster for citation: {args.citation}"
            }, indent=2))
            sys.exit(1)
    else:
        cluster_id = args.cluster_id

    result = check_negative_treatment(cluster_id, token)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
