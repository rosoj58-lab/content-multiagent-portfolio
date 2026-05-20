---
title: "SEO Content Multi-Agent Pipeline PRD Addendum"
status: "draft"
created: "2026-05-19"
updated: "2026-05-19"
---

# PRD Addendum

## Agent Responsibilities

The PRD defines product requirements, not implementation. This addendum preserves workflow mechanics for architecture.

| Agent | Responsibility | Produces |
| --- | --- | --- |
| Orchestrator Agent | Route job between stages, track status, enforce revision loop | status history, routing decisions |
| SEO Brief Agent | Convert Dry Input into SEO Brief | SEO Brief |
| Brief QA Agent | Validate brief completeness | brief QA result |
| Copywriter Agent | Generate English US article | English Original |
| Rewriter / Editor Agent | Improve structure, clarity, factual discipline | revised English Original, editorial notes |
| SEO QA Agent | Check keywords, headings, word count, intent and over-optimization | SEO QA report |
| Uniqueness QA Agent | Select uniqueness provider, accept manual score, or run optional Copyleaks check | uniqueness report |
| Spanish Localizer Agent | Localize approved English Original into Spanish | Spanish Localization |
| Italian Localizer Agent | Localize approved English Original into Italian | Italian Localization |
| French Localizer Agent | Localize approved English Original into French | French Localization |
| Final QA Agent | Verify final package completeness and status | Final QA report |

## Revision Routing

| Failure Type | Route To |
| --- | --- |
| Brief incomplete or weak | SEO Brief Agent |
| Text does not match brief | Copywriter Agent |
| Style, structure, readability issue | Rewriter / Editor Agent |
| SEO issue | SEO QA Agent + Rewriter / Editor Agent |
| Uniqueness score below 90 | Rewriter / Editor Agent |
| Translation issue | Relevant Localizer Agent |

## Confirmed Architecture Direction

- Product surface: local Streamlit app for portfolio demo.
- Workflow engine: LangGraph graph workflow.
- Data contracts: Pydantic models for brief, article, QA reports, uniqueness result and final package.
- First export formats: Markdown and JSON.
- Required uniqueness path: manual score input.
- Optional uniqueness path: Copyleaks API provider with sandbox/demo support.

## Architecture Notes To Resolve Later

- Storage model is undecided: file-based jobs or SQLite.
- LLM provider strategy is undecided: one LLM for all agents or model routing by task.
- Deterministic validators are needed for word count, required fields, score threshold and package completeness.
- Copyleaks plagiarism API is optional because real checks require credentials and async callback/webhook handling.
- The app must remain fully demoable without Copyleaks credentials.

## Uniqueness Provider Plan

Implement a provider interface:

```text
UniquenessProvider.check(text) -> UniquenessResult
```

Required providers:

- `ManualUniquenessProvider`: operator enters score and source note.
- `MockUniquenessProvider`: deterministic test/demo provider for automated tests.

Optional provider:

- `CopyleaksUniquenessProvider`: authenticates with Copyleaks, submits the English Original, records scan ID, handles sandbox mode and receives completion via webhook or local tunnel.

## Source Document Statement

The original project note explicitly states:

> Uniqueness validation is handled through external plagiarism checker API or manual score input. The system does not fake uniqueness scores.
