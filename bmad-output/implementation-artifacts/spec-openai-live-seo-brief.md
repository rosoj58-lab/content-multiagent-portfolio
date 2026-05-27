---
title: 'Add Optional OpenAI Live SEO Brief Generation'
type: 'feature'
created: '2026-05-27'
status: 'done'
baseline_commit: '41bd6ac930ae95d1d617cbcafe8e7727aac87126'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/decisions/0001-offline-first-demo-and-provider-boundaries.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent - do not modify unless human renegotiates">

## Intent

**Problem:** Текущий portfolio demo надежно показывает orchestration и QA, но весь генерируемый контент в демонстрационном пути детерминирован. На собеседовании это не доказывает, что существующая граница `LLMRunner` действительно может работать с живой моделью.

**Approach:** Добавить отдельное опциональное действие для нового job: оператор с настроенным OpenAI API key явно запускает генерацию SEO brief через OpenAI Responses API, после чего система сохраняет brief, выполняет существующий deterministic Brief QA и останавливается на ручном approval gate. Стабильный offline demo остается основным полным сценарием.

## Boundaries & Constraints

**Always:** API-вызов выполняется только после явного действия оператора и только при наличии `OPENAI_API_KEY`; ключ читается только через существующий settings boundary и никогда не пишется в артефакты или UI; модель настраивается через environment с экономным дефолтом `gpt-5.4-mini`; output проходит существующий `SEOBrief` parsing/repair contract и `BriefQAService`; live-сценарий честно маркируется как generation of brief only и оставляет approval ручным; `Run demo scenario` и тестовый offline-путь не требуют credentials.

**Ask First:** Продолжение live workflow после brief approval, реальные вызовы для article/QA/localization, отображение token usage/cost, streaming, web search/tools, хранение сырых provider responses или замена выбранной модели.

**Never:** Не вызывать OpenAI автоматически при создании job, запуске demo или в automated tests; не маскировать provider/API failure под успешный artifact; не утверждать, что live brief проверяет факты, SEO demand или завершает content package.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Настроенный live brief | Новый job и `OPENAI_API_KEY`; оператор нажимает live-action | OpenAI-generated `brief.json` и deterministic `brief_qa.json` сохранены; валидный brief переходит в `waiting_for_human` | N/A |
| Provider не настроен | Ключ отсутствует | Offline demo доступен; live-action не может инициировать сетевой вызов | UI сообщает, что для live-action нужен локальный ключ |
| API/provider error | Ключ задан, Responses API возвращает ошибку | Job остается без live brief artifact; offline demo не поврежден | Controlled error с действием проверить ключ/model и повторить |
| Невалидный structured output | Модель не возвращает `SEOBrief` после одного repair attempt | Сохраняется существующее состояние `needs_human_review`, без `brief.json` | UI показывает контролируемый результат ручной проверки |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/config.py`, `.env.example` -- already own secret/env loading; extend with configurable OpenAI model without exposing credentials.
- `src/seo_content_pipeline/services/llm_client.py`, `services/llm_runner.py` -- existing provider seam and structured repair contract; add official OpenAI Responses adapter behind it.
- `src/seo_content_pipeline/services/brief_service.py`, `brief_qa_service.py` -- existing brief generation and deterministic gate to reuse, not duplicate.
- `app.py`, `src/seo_content_pipeline/ui/components.py` -- explicit live action and truthful configured/unconfigured state beside the existing demo action.
- `tests/`, `README.md`, `docs/` -- no-network verification and interview-safe capability explanation.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `src/seo_content_pipeline/config.py`, `.env.example`, `src/seo_content_pipeline/services/llm_client.py` -- add a direct official OpenAI SDK dependency, model setting and Responses API adapter injected behind `LLMClientProtocol`.
- [x] `src/seo_content_pipeline/services/` -- compose live brief generation from the adapter, existing `BriefService`, and existing `BriefQAService`, without adding later live stages.
- [x] `app.py`, `src/seo_content_pipeline/ui/` -- expose an explicit billable live-brief action only at the new-job boundary, while retaining the complete offline demo action.
- [x] `tests/` -- test settings, fake SDK responses/failures, live orchestration, UI availability/error/result states, and prove automated tests make no network calls.
- [x] `README.md`, `docs/`, `CHANGELOG.md` -- document setup, cost/secret boundary and the honest limit that only SEO brief generation is live.

**Acceptance Criteria:**
- Given a newly created job and configured fake OpenAI client response, when live brief generation is triggered in tests, then the same job persists a validated brief/QA trail and stops at manual approval.
- Given no API key or a provider exception, when the operator sees or invokes the live surface, then no successful live brief artifact is produced and the stable offline demo remains usable.
- Given the existing BP/LP/GP offline scenarios, when the release gate runs without credentials, then their established outcomes remain unchanged.

## Spec Change Log

## Design Notes

The official OpenAI model catalog identifies `gpt-5.4-mini` as the lower-cost GPT-5.4 variant and documents Responses API plus Structured Outputs support. This feature uses the existing JSON/Pydantic repair boundary rather than claiming a new production-grade structured-output integration. Sources: `https://developers.openai.com/api/docs/models/gpt-5.4-mini`, `https://developers.openai.com/api/docs/models`.

## Verification

**Commands:**
- `uv run ruff check .` -- expected: adapter, UI and tests pass lint.
- `uv run pytest` -- expected: provider is fully mocked; no OpenAI credentials or network required.
- `make --no-print-directory release-check` -- expected: existing offline demo outcomes and portfolio gate pass unchanged.

## Suggested Review Order

**Live Workflow Boundary**

- Reuses existing brief and QA services while stopping before later live stages.
  [`live_brief_service.py:23`](../../Content_MultiAgent/src/seo_content_pipeline/services/live_brief_service.py#L23)

- Restricts generation to a configured, newly created job.
  [`live_brief_service.py:37`](../../Content_MultiAgent/src/seo_content_pipeline/services/live_brief_service.py#L37)

**Provider Integration**

- Isolates the explicit Responses API request and disables provider response storage.
  [`llm_client.py:24`](../../Content_MultiAgent/src/seo_content_pipeline/services/llm_client.py#L24)

- Adds a configurable low-cost default model without exposing the API key.
  [`config.py:24`](../../Content_MultiAgent/src/seo_content_pipeline/config.py#L24)

**Operator Surface**

- Keeps offline demo intact while exposing a separate live-only action.
  [`app.py:63`](../../Content_MultiAgent/app.py#L63)

- Makes the optional paid action and missing configuration visible.
  [`components.py:76`](../../Content_MultiAgent/src/seo_content_pipeline/ui/components.py#L76)

**Verification And Documentation**

- Tests manual-gate success, missing-key handling and invalid structured output.
  [`test_live_brief_service.py:53`](../../Content_MultiAgent/tests/test_live_brief_service.py#L53)

- Verifies UI availability, success boundary and controlled failures with fakes.
  [`test_app_shell.py:152`](../../Content_MultiAgent/tests/test_app_shell.py#L152)

- Documents local setup and the honest brief-only live limitation.
  [`README.md:86`](../../Content_MultiAgent/README.md#L86)
