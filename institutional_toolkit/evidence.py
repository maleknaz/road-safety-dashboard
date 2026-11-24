"""Country-scoped retrieval over the *real, unmodified* five repository datasets.

A source-linked plan is not proof of implementation. Zero records mean that the
REVIEWED SUBSET lacks evidence, never that a government lacks a programme.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit
import csv, json, math, re

FILES = ("countries_195.json", "checklist.csv", "institutional_evidence.csv", "source_findings.csv", "intervention_evidence.csv")


def url(value: str) -> str:
    """Return the first safe URL from potentially multi-valued legacy cells."""
    for piece in re.split(r"\s*[|;,]\s*(?=https?://)", str(value or "")):
        u = piece.strip().split()[0] if piece.strip() else ""
        p = urlsplit(u)
        if p.scheme in ("https", "http") and p.netloc and not any(x in u for x in ('<', '>', '"', "'")):
            return u
    return ""


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=4)
def load_data(folder: str) -> dict:
    root = Path(folder)
    missing = [f for f in FILES if not (root / f).is_file()]
    if missing:
        raise FileNotFoundError("Missing required research files: " + ", ".join(missing))
    countries = json.loads((root / "countries_195.json").read_text(encoding="utf-8"))
    checklist = [r for r in read_csv(root / "checklist.csv") if r.get("eligible", "").lower() == "true"]
    institutional = read_csv(root / "institutional_evidence.csv")
    interventions = read_csv(root / "intervention_evidence.csv")
    findings = read_csv(root / "source_findings.csv")
    mechanisms = {}
    for r in interventions:
        pid = r["profile_id"]
        mechanisms[pid] = {"profile_id": pid, "country": r["country"], "jurisdiction": r["jurisdiction"],
                            "coordinating_body": r["coordinating_body"]}
    domains = list(dict.fromkeys(r["domain"] for r in checklist))
    return {"countries": countries, "checklist": checklist, "domains": domains,
            "institutional": institutional, "interventions": interventions,
            "findings": findings, "mechanisms": list(mechanisms.values())}


def country_context(data: dict, country: str) -> dict:
    """Gather mechanisms and both per-item and source-specific evidence.

    Preserve subnational jurisdiction labels. Never silently claim that a
    subnational study represents a national performance finding.
    """
    mechanisms = [p for p in data["mechanisms"] if p["country"] == country]
    ids = {p["profile_id"] for p in mechanisms}
    return {
        "country": country, "mechanisms": mechanisms,
        "institutional": [r for r in data["institutional"] if r["profile_id"] in ids],
        "interventions": [r for r in data["interventions"] if r["profile_id"] in ids and r.get("eligible", "").lower() == "true"],
        "findings": [r for r in data["findings"] if r["profile_id"] in ids],
    }


def sources_for(context: dict) -> list[dict]:
    out = []; keys = set()
    for kind in ("institutional", "findings", "interventions"):
        for r in context[kind]:
            link = url(r.get("source_url", ""))
            if not link: continue
            fingerprint = (r.get("profile_id"), r.get("matrix_id", r.get("domain")), link)
            if fingerprint in keys: continue
            keys.add(fingerprint)
            out.append({"url": link, "kind": kind,
                        "profile_id": r.get("profile_id", ""),
                        "matrix_id": r.get("matrix_id", ""),
                        "domain": r.get("domain", ""),
                        "document": r.get("evidence_document", ""),
                        "checked_on": r.get("checked_on") or r.get("review_date") or ""})
    return out


def coverage(data: dict, country: str) -> dict:
    ctx = country_context(data, country)
    cited_domains = {r["domain"] for r in ctx["institutional"] if url(r.get("source_url", ""))}
    cited_items = {r["matrix_id"] for kind in ("interventions", "findings") for r in ctx[kind]
                   if url(r.get("source_url", "")) and r.get("matrix_id") in {i["matrix_id"] for i in data["checklist"]}}
    return {"Country": country, "Reviewed mechanisms": len(ctx["mechanisms"]),
            "Institutional domains with sources": len(cited_domains),
            "Source-linked checklist items": len(cited_items),
            "Total domains": len(data["domains"]),
            "Total eligible interventions": len(data["checklist"])}


def all_coverage(data: dict) -> list[dict]:
    return [coverage(data, c) for c in data["countries"]]


def selected_record(group: list[dict]) -> dict:
    """Prefer source-linked and recently checked source-specific records."""
    return sorted(group, key=lambda r: (bool(url(r.get("source_url", ""))), bool(r.get("checked_on", "")),
                                        bool(r.get("documented_action", ""))), reverse=True)[0] if group else {}


def checklist_prefill(data: dict, country: str, responses: dict | None = None) -> list[dict]:
    ctx = country_context(data, country)
    responses = responses or {}
    by_key = defaultdict(list)
    for kind in ("findings", "interventions"):
        for r in ctx[kind]:
            if r.get("matrix_id"): by_key[r["matrix_id"]].append(r)
    out = []
    for item in data["checklist"]:
        key = item["matrix_id"]
        records = by_key[key]
        sourced = [r for r in records if url(r.get("source_url", ""))]
        best = selected_record(sourced or records)
        srcs = sorted({url(r.get("source_url", "")) for r in sourced})
        reports = sorted({r.get("assessment", "") for r in sourced if r.get("assessment")})
        status = ("Source classifications differ; verify interpretation" if len(reports) > 1
                  else best.get("assessment", "Not reviewed") if sourced
                  else "No source-specific evidence verified in this research subset")
        answer = responses.get(key, {})
        explanation = (best.get("verification_boundary") or best.get("audit_rationale") or
                       best.get("rationale") or best.get("implementation_conclusion") or "")
        user_answer = answer.get("choice", "Not answered")
        if len(reports) > 1:
            next_step = "Reconcile differences in existing source classifications, scope and dates before assessing implementation. "
        elif sourced:
            next_step = "Confirm that the cited activity and responsible institution remain current. Obtain evidence of actual implementation, not only the strategy or plan. "
        else:
            next_step = "Ask the responsible public authority whether this intervention exists and request its official documentation. Do not assume it is absent. "
        next_step += ("For '" + item["ideal_intervention"] + "', identify the accountable entity, "
                      "current policy or operational document, measurable deliverable and evidence of completion.")
        if user_answer == "I believe it does not exist":
            next_step = "The respondent suspects a gap; verify formally before classifying it as confirmed. " + next_step
        elif user_answer == "Yes, with official documentation" and not answer.get("source"):
            next_step = "Request the official document link or reference to corroborate the respondent's answer. " + next_step
        out.append({"matrix_id": key, "pillar": item["pillar"], "domain": item["domain"],
                    "ideal_task": item["ideal_task"], "ideal_intervention": item["ideal_intervention"],
                    "research_status": status, "evidence_note": explanation,
                    "documented_action": best.get("documented_action", ""),
                    "responsible_institution": best.get("responsible_institution", ""),
                    "implementation_stage": best.get("activity_stage", "Not verified"),
                    "source_urls": srcs,
                    "source_locator": best.get("source_locator", ""),
                    "last_checked": best.get("checked_on") or best.get("review_date") or "",
                    "reviewed_mechanisms": sorted({r.get("profile_id", "") for r in records}),
                    "respondent_answer": user_answer, "respondent_note": answer.get("note", ""),
                    "respondent_source": answer.get("source", ""),
                    "assessment_status": "Draft, not government validated",
                    "recommended_next_step": next_step})
    return out


def questionnaire(data: dict, country: str, count: int = 8) -> list[dict]:
    """One per pillar in pass 1, then distinct domains; avoid asking 72 upfront."""
    rows = checklist_prefill(data, country)
    unknown = [r for r in rows if not r["source_urls"]]
    candidates = unknown or rows
    chosen = []; seen_pillars = set(); seen_domains = set()
    for r in candidates:
        if r["pillar"] not in seen_pillars:
            chosen.append(r);seen_pillars.add(r["pillar"]);seen_domains.add(r["domain"])
            if len(chosen) == count:return chosen
    for r in candidates:
        if r["matrix_id"] not in {x["matrix_id"] for x in chosen} and r["domain"] not in seen_domains:
            chosen.append(r);seen_domains.add(r["domain"])
            if len(chosen) == count:return chosen
    return (chosen + [r for r in candidates if r["matrix_id"] not in {x["matrix_id"] for x in chosen}])[:count]


def compare(data: dict, first: str, second: str) -> list[dict]:
    x = country_context(data, first);y=country_context(data, second)
    out=[]
    for domain in data["domains"]:
        def info(ctx):
            rs=[r for r in ctx["institutional"] if r["domain"] == domain]
            source=[r for r in rs if url(r.get("source_url", ""))]
            main=selected_record(source or rs)
            return {"evidence": "Linked institutional record" if source else "Not verified by a linked institutional record",
                    "responsible_institution":main.get("responsible_institution", ""),
                    "membership":main.get("formal_membership", "Not verified"),
                    "functional_responsibility":main.get("functional_responsibility", "Not verified"),
                    "implementation_evidence":main.get("implementation_evidence", "Not verified"),
                    "source_url": url(main.get("source_url", "")),
                    "rationale":main.get("classification_rationale", "")}
        out.append({"domain":domain,first:info(x),second:info(y)})
    return out


def _tokens(s: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[\w\-]{3,}", s or "", re.UNICODE)}


def retrieve(data: dict, country: str, question: str, limit: int = 10) -> list[dict]:
    """Local lexical retrieval over grounded source excerpts (no API or new search)."""
    ctx=country_context(data,country)
    query=_tokens(question)
    found=[]
    for kind in ("institutional", "findings", "interventions"):
        for row in ctx[kind]:
            source = url(row.get("source_url", ""))
            if not source: continue
            snippet = " | ".join(str(row.get(k,"")) for k in (
                "domain","coordinating_body","responsible_institution","formal_membership",
                "functional_responsibility","ideal_intervention","documented_action",
                "case_evidence","verification_boundary","rationale","classification_rationale") if row.get(k))
            terms = _tokens(snippet)
            match = query & terms
            score = sum(1 + math.log(1 + len(w)) for w in match) + (1 if kind == "findings" else 0)
            if score:
                found.append({"kind":kind,"source_url":source,"country":country,
                              "profile_id":row.get("profile_id", ""),"matrix_id":row.get("matrix_id", ""),
                              "snippet":snippet[:1300],"score":score})
    found.sort(key=lambda r:-r["score"])
    seen = set();output=[]
    for r in found:
        key=(r["source_url"],r["matrix_id"],r["profile_id"])
        if key not in seen:
            seen.add(key);output.append(r)
        if len(output)>=limit: break
    return output


def validate(data: dict) -> dict:
    ids={r["matrix_id"] for r in data["checklist"]}
    pids={r["profile_id"] for r in data["mechanisms"]}
    return {"countries":len(data["countries"]),"domains":len(data["domains"]),
            "eligible_interventions":len(data["checklist"]),"researched_mechanisms":len(data["mechanisms"]),
            "countries_with_reviewed_mechanisms":len(set(r["country"] for r in data["mechanisms"])),
            "institutional_records":len(data["institutional"]),
            "intervention_matrix_rows":len(data["interventions"]),
            "source_specific_findings":len(data["findings"]),
            "unrecognized_intervention_ids":sorted({r["matrix_id"] for r in data["findings"] if r["matrix_id"] not in ids}),
            "orphan_source_records":sum(r["profile_id"] not in pids for r in data["findings"]),
            "audited_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
