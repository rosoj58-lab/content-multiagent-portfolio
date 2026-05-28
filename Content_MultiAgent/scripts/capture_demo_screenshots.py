"""Capture portfolio demo screenshots from the local Streamlit app."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, TimeoutError, expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "artifacts" / "demo" / "demo-summary.json"
OUTPUT_DIR = ROOT / "docs" / "assets" / "screenshots"
APP_URL = os.environ.get("APP_URL", "http://localhost:8501")


def main() -> None:
    """Open the app and capture the key portfolio states."""
    summary = _load_summary()
    bp_job_id = _job_id(summary, "bp")
    lp_job_id = _job_id(summary, "lp")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=30_000)
        _wait_for_app(page)
        _capture(page, "01-home-recent-jobs.png")

        _load_recent_job(page, bp_job_id)
        _expand_if_present(page, "Artifacts")
        _scroll_to_text(page, "Decision QA Scorecard")
        _capture(page, "02-bp-scorecard-timeline.png")

        _expand_if_present(page, "Debug Snapshot")
        _scroll_to_text(page, "Debug Snapshot")
        _capture(page, "03-debug-snapshot-artifact.png")

        _load_recent_job(page, lp_job_id)
        _scroll_to_text(page, "Replacement statement")
        _capture(page, "04-lp-revision-path.png")
        browser.close()


def _load_summary() -> dict[str, Any]:
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


def _job_id(summary: dict[str, Any], demo: str) -> str:
    for run in summary["runs"]:
        if run["demo"] == demo:
            return str(run["job_id"])
    raise RuntimeError(f"Demo run not found: {demo}")


def _wait_for_app(page: Page) -> None:
    expect(page.get_by_text("SEO Content Pipeline")).to_be_visible(timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=10_000)


def _load_recent_job(page: Page, job_id: str) -> None:
    selector = page.locator('[data-testid="stSelectbox"]').filter(has_text="Recent jobs").first
    expect(selector).to_be_visible(timeout=10_000)
    selector.click()
    page.keyboard.press("Meta+A")
    page.keyboard.type(job_id)
    page.keyboard.press("Enter")
    page.get_by_role("button", name="Load selected job").click()
    expect(page.get_by_text(f"Job created: {job_id}")).to_be_visible(timeout=20_000)
    page.wait_for_load_state("networkidle", timeout=10_000)


def _expand_if_present(page: Page, label: str) -> None:
    expander = page.locator("details").filter(has_text=label).first
    try:
        expander.wait_for(state="attached", timeout=5_000)
    except TimeoutError:
        return
    expander.scroll_into_view_if_needed(timeout=5_000)
    if expander.get_attribute("open") is None:
        expander.locator("summary").click()
        expect(expander).to_have_attribute("open", "", timeout=5_000)


def _scroll_to_text(page: Page, text: str) -> None:
    target = page.get_by_text(text, exact=True).last
    expect(target).to_be_attached(timeout=10_000)
    target.evaluate("element => element.scrollIntoView({block: 'start', inline: 'nearest'})")
    page.evaluate("window.scrollBy(0, -72)")
    page.wait_for_timeout(500)


def _capture(page: Page, filename: str) -> None:
    page.screenshot(path=str(OUTPUT_DIR / filename), full_page=False)


if __name__ == "__main__":
    main()
