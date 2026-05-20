---
title: "SEO Content Multi-Agent Pipeline"
status: "draft"
created: "2026-05-19"
updated: "2026-05-19"
sources:
  - "/Users/irinawork/Downloads/SEO Content Multi-Agent Pipeline.docx"
  - "/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/briefs/brief-Content-Multi-Agent-2026-05-19/brief.md"
  - "/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/briefs/brief-Content-Multi-Agent-2026-05-19/addendum.md"
---

# PRD: SEO Content Multi-Agent Pipeline

## 0. Document Purpose

Этот PRD описывает MVP мультиагентной системы для производства SEO-контента. Документ нужен для дальнейших BMad-шагов: architecture, epics/stories и implementation planning. Требования сгруппированы по capability, functional requirements имеют стабильные ID `FR-N`, а неподтвержденные решения помечены `[ASSUMPTION]`.

## 1. Vision

SEO Content Multi-Agent Pipeline должен заменить ручной копирайтинг управляемым агентным workflow: из сухого входного текста система создает SEO-бриф, пишет English US original, проверяет качество, принимает uniqueness score из внешнего источника или manual input, локализует контент на Spanish, Italian и French и собирает финальный QA-пакет.

MVP должен демонстрировать не только генерацию текста, но и контроль качества: понятные статусы, ревизионные циклы, проверку SEO-требований, проверку объема, честное handling уникальности и final status `Approved` / `Needs Revision`. Первый портфолио-релиз строится как local Streamlit app с LangGraph workflow и pluggable uniqueness provider.

## 2. Target User

### 2.1 Primary Persona

SEO-специалист, контент-менеджер или владелец small agency, которому нужно быстро создавать многоязычный SEO-контент без ручного копирайтера, но с достаточным контролем качества для клиентской или портфолио-демонстрации.

### 2.2 Jobs To Be Done

- Когда есть сухой исходный текст, пользователь хочет получить SEO-ready article package без самостоятельного написания и ручной проверки каждого этапа.
- Когда контент нужно показать клиенту или в портфолио, пользователь хочет иметь артефакты процесса: brief, article, translations, QA reports, uniqueness result.
- Когда проверка провалилась, пользователь хочет видеть причину и понимать, какой этап нужно переделать.

### 2.3 Non-Users for MVP

- Enterprise content teams needing approval workflows, SSO, roles, and audit compliance.
- Publishers requiring automated CMS publishing.
- SEO teams requiring live SERP scraping and production keyword research.

### 2.4 Key User Journeys

- **UJ-1. Operator creates a BP content package from dry input.** Operator opens the local Streamlit app, selects Blog Post or lets the system infer it, pastes dry source text, reviews the generated SEO brief, approves it, receives English US article, runs uniqueness through the selected provider or enters manual score, and downloads the final package with translations and QA report.

- **UJ-2. Operator handles failed uniqueness check.** Operator receives a uniqueness score below 90%, enters it into the system, sees status `Needs Revision`, and the workflow returns the English original to rewriting before localization continues.

- **UJ-3. Operator prepares portfolio demos for three article types.** Operator runs BP, LP and GP demo inputs through the same pipeline and receives comparable final packages that demonstrate type-specific output and QA.

## 3. Glossary

- **Dry Input** — исходный сухой текст, заметки или факты, из которых система строит SEO-бриф и статью.
- **Article Type** — один из MVP-типов: `BP`, `LP`, `GP`.
- **BP** — Blog Post, информационная SEO-статья.
- **LP** — Landing Page, коммерческий SEO-лендинг.
- **GP** — Guest Post, статья для link building с нативным link placement.
- **SEO Brief** — структурированное задание для генерации статьи: тема, цель, audience, keywords, LSI, структура, tone of voice и ограничения.
- **English Original** — первичная статья на English US, созданная по approved SEO Brief.
- **Localization** — перевод и локальная адаптация English Original на Spanish, Italian или French.
- **Uniqueness Provider** — selected mechanism for uniqueness validation: manual input in base MVP, optional Copyleaks API integration when credentials and async callback setup are available.
- **Uniqueness Score** — процент уникальности из Uniqueness Provider.
- **Final Content Package** — итоговый набор артефактов: brief, English Original, translations, SEO QA report, uniqueness report и final status.
- **Revision Loop** — возврат задачи на предыдущий этап при провале QA.

## 4. Features

### 4.1 Content Intake and Article Type Selection

**Description:** Пользователь передает Dry Input и выбирает Article Type или просит систему определить его. Система создает job со статусом `Input Received` и сохраняет входные данные для downstream agents. Realizes UJ-1, UJ-3.

**Functional Requirements:**

#### FR-1: Accept Dry Input

Operator can submit Dry Input for a new content job.

**Consequences:**
- System accepts plain text input.
- System rejects empty input with a clear validation message.
- System stores the original Dry Input as part of the job record.

#### FR-2: Select or Infer Article Type

Operator can select `BP`, `LP`, or `GP`; if no type is selected, the system can infer a proposed Article Type and expose it for confirmation. `[ASSUMPTION: inference is allowed in MVP, but confirmation remains available.]`

**Consequences:**
- System supports exactly `BP`, `LP`, and `GP` in MVP.
- System records the final Article Type before brief approval.
- System applies type-specific QA expectations.

### 4.2 SEO Brief Generation and QA

**Description:** The SEO Brief Agent creates the SEO Brief from Dry Input and Article Type. The Brief QA Agent checks whether the brief is sufficient for article generation. Realizes UJ-1.

**Functional Requirements:**

#### FR-3: Generate SEO Brief

System generates an SEO Brief containing topic, goal, audience, main keyword, secondary keywords, LSI keywords, H1/H2/H3 outline, tone of voice and constraints.

**Consequences:**
- SEO Brief includes all required fields.
- SEO Brief is tied to the selected Article Type.
- SEO Brief status becomes `Brief Drafted`.

#### FR-4: Validate SEO Brief Completeness

System validates that the SEO Brief contains enough information for article generation.

**Consequences:**
- If the brief passes, status becomes `Brief Approved`.
- If the brief fails, system returns the job to SEO Brief Agent with specific missing or weak fields.
- Brief QA does not approve a brief with missing main keyword, unclear audience, or no outline.

### 4.3 English Article Generation and Editorial QA

**Description:** The Copywriter Agent writes the English Original. The Rewriter / Editor Agent checks structure, task fit, readability, factual discipline and removes weak content. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-5: Generate English US Original

System generates an English US article from an approved SEO Brief.

**Consequences:**
- Output language is English US.
- Target length is 1500-1600 words.
- Output uses H1/H2/H3 structure.
- Status moves through `Writing` to `Editorial Review`.

#### FR-6: Run Editorial QA

System checks the English Original for brief compliance, logical structure, readability, lack of filler and unsupported factual claims.

**Consequences:**
- If editorial QA passes, job proceeds to SEO QA.
- If editorial QA fails, job returns to Copywriter Agent or Rewriter / Editor Agent with concrete revision notes.
- Editorial QA must flag claims not supported by Dry Input or SEO Brief unless clearly generic and low-risk.

### 4.4 SEO QA

**Description:** The SEO QA Agent checks whether the English Original satisfies SEO requirements without over-optimization. Realizes UJ-1, UJ-3.

**Functional Requirements:**

#### FR-7: Check SEO Requirements

System checks main keyword usage, secondary keyword usage, LSI coverage, headings, word count, intent match, Article Type fit and keyword stuffing risk.

**Consequences:**
- Word count is computed programmatically or by deterministic parser, not only by LLM judgment.
- System produces an SEO QA report with pass/fail per check.
- If SEO QA fails, job returns to SEO QA + Rewriter with revision notes.

### 4.5 Uniqueness Handling

**Description:** The system does not fake uniqueness. It accepts Uniqueness Score from manual input in base MVP and supports optional external checker integration as a pluggable provider. Localization is gated on the threshold. Realizes UJ-2.

**Functional Requirements:**

#### FR-8: Select Uniqueness Provider

Operator can select manual uniqueness input or an enabled external plagiarism checker provider.

**Consequences:**
- Manual provider is always available.
- Copyleaks provider is available only when required credentials and callback configuration are present.
- Disabled providers are visible as unavailable with a clear setup message.

#### FR-9: Accept Manual Uniqueness Score

Operator can enter a Uniqueness Score for the English Original.

**Consequences:**
- System accepts numeric score from 0 to 100.
- System rejects invalid values.
- System records score source as `manual`.

#### FR-10: Run Copyleaks Plagiarism Check

System can submit the English Original to Copyleaks for plagiarism checking when Copyleaks provider is enabled. `[OPTIONAL for portfolio MVP]`

**Consequences:**
- System authenticates with Copyleaks using environment variables, never hardcoded secrets.
- System submits text as a file scan and records scan ID.
- System supports sandbox mode for demo/testing.
- System handles async completion through webhook or a documented local tunnel setup.
- If Copyleaks is unavailable, system falls back to manual provider without blocking the rest of the workflow.

#### FR-11: Gate Workflow by Uniqueness Threshold

System allows localization only when Uniqueness Score is at least 90%.

**Consequences:**
- Score `>= 90` moves job to `Localization`.
- Score `< 90` moves job to `Needs Revision` and routes back to Rewriter / Editor Agent.
- The final report includes the exact score and source.

### 4.6 Localization

**Description:** After English Original passes QA and uniqueness gate, localizer agents create Spanish, Italian and French versions. Realizes UJ-1, UJ-3.

**Functional Requirements:**

#### FR-12: Generate Spanish Localization

System generates Spanish Localization from the approved English Original.

**Consequences:**
- Spanish output preserves meaning, headings and SEO intent.
- Spanish output adapts wording to selected geo when provided. `[ASSUMPTION: default Spanish geo is unresolved.]`

#### FR-13: Generate Italian Localization

System generates Italian Localization from the approved English Original.

**Consequences:**
- Italian output preserves meaning, headings and SEO intent.
- Italian output is created only after English Original passes uniqueness gate.

#### FR-14: Generate French Localization

System generates French Localization from the approved English Original.

**Consequences:**
- French output preserves meaning, headings and SEO intent.
- French output is created only after English Original passes uniqueness gate.

### 4.7 Final QA and Content Package

**Description:** The Final QA Agent verifies all required artifacts and produces final status. Realizes UJ-1, UJ-3.

**Functional Requirements:**

#### FR-15: Assemble Final Content Package

System assembles SEO Brief, English Original, Spanish Localization, Italian Localization, French Localization, SEO QA report, uniqueness report and final status.

**Consequences:**
- Missing required artifact prevents `Approved` status.
- Package format is exportable as Markdown and JSON in MVP.

#### FR-16: Produce Final QA Report

System produces a final QA report with status `Approved` or `Needs Revision`.

**Consequences:**
- Report lists completed stages, failed checks if any, uniqueness result and localization status.
- `Approved` requires all mandatory checks to pass.
- `Needs Revision` includes routing guidance to the next agent/stage.

### 4.8 Workflow Status and Revision Loop

**Description:** Orchestrator Agent tracks statuses and routes failed checks to the correct stage.

**Functional Requirements:**

#### FR-17: Track Workflow Status

System tracks job status using the defined status set.

**Consequences:**
- Supported statuses: `Input Received`, `Brief Drafted`, `Brief Approved`, `Writing`, `Editorial Review`, `SEO QA`, `Uniqueness Check`, `Localization`, `Final QA`, `Approved`, `Needs Revision`.
- Status changes are recorded in order.

#### FR-18: Route Failed Checks

System routes failed checks according to revision loop rules.

**Consequences:**
- Brief problem returns to SEO Brief Agent.
- Text problem returns to Copywriter Agent.
- Style or structure problem returns to Rewriter / Editor Agent.
- SEO problem returns to SEO QA + Rewriter.
- Uniqueness below 90 returns to Rewriter / Editor Agent.
- Localization problem returns to the relevant Localizer Agent.

## 5. Cross-Cutting NFRs

- **NFR-1 Quality transparency:** every QA stage must produce a short machine-readable or structured report.
- **NFR-2 Deterministic checks where possible:** word count, score threshold, required artifact presence and status validation should be deterministic.
- **NFR-3 Traceability:** final package should reference the Dry Input, Article Type, SEO Brief and QA reports used to create it.
- **NFR-4 Cost control:** MVP should avoid unnecessary repeated full-article generation when only a targeted revision is needed. `[ASSUMPTION: exact LLM provider and token budget are unresolved.]`
- **NFR-5 Human override:** operator can review and correct key intermediate artifacts before continuing; brief approval remains a manual gate.
- **NFR-6 Secret handling:** API keys and provider credentials must be read from environment variables or local ignored config, never committed.
- **NFR-7 Portfolio reliability:** the app must run end-to-end without Copyleaks credentials by using manual uniqueness input.

## 6. Non-Goals

- The MVP will not perform AI-content detection.
- The MVP will not claim to verify uniqueness by itself.
- The base MVP will not require plagiarism checker API credentials to run.
- The MVP will not perform live SERP scraping or full keyword research.
- The MVP will not publish directly to CMS.
- The MVP will not support article types beyond BP, LP and GP.
- The MVP will not provide enterprise user management, approvals or billing.

## 7. MVP Scope

### 7.1 In Scope

- Dry Input submission.
- Article Type selection or confirmation.
- SEO Brief generation.
- Brief QA.
- English US article generation.
- Editorial QA.
- SEO QA.
- Manual uniqueness score input.
- Optional Copyleaks uniqueness provider with sandbox/demo support.
- Localization to Spanish, Italian and French.
- Final QA report.
- Markdown and JSON final package.
- Three demo cases: BP, LP, GP.

### 7.2 Out of Scope for MVP

- Other plagiarism checker integrations beyond Copyleaks, deferred to v2.
- Client dashboard, deferred until after demo validation.
- Bulk job queue, deferred until repeat usage is proven.
- CMS export, deferred until a target CMS is selected.
- Brand style profiles, deferred unless demos require them.

## 8. Success Metrics

**Primary**

- **SM-1:** Demo completion rate - all three demo cases produce complete Final Content Packages. Validates FR-1 through FR-18.
- **SM-2:** QA gate accuracy - final status never becomes `Approved` when a mandatory artifact or score is missing. Validates FR-11, FR-15, FR-16, FR-17.
- **SM-3:** Word count compliance - approved English Originals are within 1500-1600 words. Validates FR-5, FR-7.

**Secondary**

- **SM-4:** Revision clarity - failed QA stages include actionable routing guidance. Validates FR-6, FR-7, FR-11, FR-16, FR-18.
- **SM-5:** Localization completeness - approved packages include Spanish, Italian and French outputs. Validates FR-12, FR-13, FR-14, FR-15.
- **SM-6:** Offline demo reliability - workflow completes with manual uniqueness provider when no Copyleaks credentials exist. Validates FR-8, FR-9, FR-11.

**Counter-metrics**

- **SM-C1:** Do not optimize for article volume if QA failures rise; more generated text is not success without approved packages.
- **SM-C2:** Do not optimize for passing uniqueness by hiding or inventing scores; uniqueness source must remain explicit.

## 9. Risks and Mitigations

- **Unsupported facts:** LLM may invent claims. Mitigation: Editorial QA flags unsupported claims and prompts should prefer Dry Input-grounded facts.
- **False SEO confidence:** LLM-generated keywords may not reflect real search demand. Mitigation: label keyword generation as MVP-only unless user supplies target keywords.
- **External checker complexity:** real plagiarism APIs can require credentials, credits and async callback setup. Mitigation: make Copyleaks optional and keep manual provider as a reliable fallback.
- **Translation quality drift:** localizations may preserve words but lose intent. Mitigation: Final QA checks required language outputs and headline/intent preservation.
- **Local webhook complexity:** Copyleaks plagiarism scanning is async and webhook-oriented. Mitigation: support sandbox mode and document local tunnel setup for the portfolio demo.

## 10. Open Questions

1. Which LLM/provider should be used first?
2. Should the system store job history and revision logs in v1?
3. Should the user provide keywords, or should the system generate keywords from Dry Input?
4. What is the default Spanish geo: Spain, Mexico, LATAM, or user-selected per job?
5. Should Copyleaks integration be implemented in the first coding pass or after the manual provider is working?

## 11. Assumptions Index

- §4.1 FR-2: Article Type inference is allowed, but confirmation remains available.
- §4.6 FR-12: Default Spanish geo is unresolved.
- §5 NFR-4: LLM provider and token budget are unresolved.
