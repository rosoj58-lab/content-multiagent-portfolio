---
title: 'Show a Decision QA Scorecard for Demo Scenarios'
type: 'feature'
created: '2026-05-25'
status: 'done'
baseline_commit: 'aad95cb0a54e1a533e4ef23cfe64ac38759f36a9'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/demo-script.md'
---

<frozen-after-approval reason="human-owned intent - do not modify unless human renegotiates">

## Intent

**Problem:** Демонстрационные сценарии уже принимают разные решения (`approved`, `needs_revision`, `needs_human_review`), но интерфейс показывает в основном статус и сырой artifact. На собеседовании пользователю приходится вручную открывать JSON, чтобы объяснить, какой контроль качества сработал и что делать дальше.

**Approach:** Добавить в Streamlit компактный Decision QA Scorecard, собираемый из сохраненных типизированных artifacts. Карточка должна одинаково понятно объяснять успешный BP-путь и остановки LP/GP, не перенося бизнес-логику принятия решений в UI.

## Boundaries & Constraints

**Always:** Использовать persisted artifacts как источник истины; построение view-model держать отдельно от Streamlit-rendering; отображать outcome, decision stage, проверяемые сигналы и next action/recommendations; сохранить воспроизводимость трех offline demo scenarios.

**Ask First:** Изменение самих правил QA, статусов маршрутизации, demo-текстов или состава pipeline stages; добавление нового внешнего сервиса либо LLM-вызова ради scorecard.

**Never:** Не вычислять новый quality verdict в UI; не скрывать failing checks за общим сообщением; не превращать artifact JSON в единственный пользовательский способ понять решение; не добавлять dashboard истории jobs в рамках этой задачи.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| BP approval | Job с `status=approved` и `final_qa_report.json` | Scorecard показывает approval, финальную стадию, uniqueness/localization readiness и отсутствие blocking action | N/A |
| LP revision | Job с `status=needs_revision` и failed `editorial_qa.json` | Scorecard показывает failed claim check, рекомендацию убрать или доказать 70 percent claim и маршрут в writing | N/A |
| GP human review | Job с `status=needs_human_review` и editorial report | Scorecard показывает необходимость редакторского решения по link placement и human-review action | N/A |
| No decision yet | Новый job без decision artifact | Scorecard не отображается до появления решения | Не показывать ошибку |

</frozen-after-approval>

## Code Map

- `app.py` -- подключает UI-панели текущего job и должен вызвать scorecard после чтения persisted state.
- `src/seo_content_pipeline/ui/renderers.py` -- существующие QA checklist helpers; источник паттерна для человекочитаемого отображения checks.
- `src/seo_content_pipeline/models/qa_result.py` -- контракт editorial decision для LP/GP.
- `src/seo_content_pipeline/models/final_qa.py` -- контракт approved final decision для BP.
- `src/seo_content_pipeline/services/artifact_store.py` -- единый доступ к persisted decision artifacts.
- `tests/test_demo_observability.py` и `tests/test_app_shell.py` -- pure builder и Streamlit outcome coverage.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/ui/qa_scorecard.py` -- добавить UI-ready scorecard builder и тонкий renderer для final/editorial decision artifacts.
- [x] `app.py` -- отображать scorecard текущего job после выполнения scenario и на последующем rerender.
- [x] `tests/test_demo_observability.py`, `tests/test_app_shell.py` -- проверить BP, LP, GP и отсутствие решения до запуска.
- [x] `README.md`, `docs/demo-script.md`, `docs/interview-cheatsheet.md` -- обновить walkthrough, чтобы scorecard стал частью показа качества.

**Acceptance Criteria:**
- Given успешно завершенный BP demo job, when оператор открывает его в Streamlit, then scorecard показывает `approved`, final QA evidence, uniqueness readiness и localization readiness без действия по исправлению.
- Given LP demo job с неподтвержденным claim, when scorecard построен из `editorial_qa.json`, then видны `needs_revision`, failed check, рекомендация и routing target `writing`.
- Given GP demo job, when scorecard построен из `editorial_qa.json`, then видны `needs_human_review`, причина editorial judgment и действие для человека.
- Given только созданный job без decision artifact, when интерфейс рендерится, then scorecard отсутствует и существующие timeline/artifact панели продолжают работать.

## Spec Change Log

## Design Notes

У approved и routed сценариев разные decision artifacts: BP заканчивается `FinalQAReport`, LP/GP - `QAReport`. Scorecard должен нормализовать их в один UI-facing view-model; Streamlit только отображает готовые строки и checklist rows. Это сохраняет архитектурную границу: решение остается в сервисах и artifacts, а UI делает его понятным.

## Verification

**Commands:**
- `uv run ruff check .` -- expected: lint passes.
- `uv run pytest tests/test_demo_observability.py tests/test_app_shell.py` -- expected: builder and UI scenarios pass.
- `make --no-print-directory release-check` -- expected: all tests pass and BP/LP/GP artifacts regenerate with distinct outcomes.

## Suggested Review Order

**Decision Model**

- Normalize persisted final and editorial decisions into one UI-facing scorecard.
  [`qa_scorecard.py:52`](../../Content_MultiAgent/src/seo_content_pipeline/ui/qa_scorecard.py#L52)

- Render evidence, route and next action without recomputing workflow decisions.
  [`qa_scorecard.py:152`](../../Content_MultiAgent/src/seo_content_pipeline/ui/qa_scorecard.py#L152)

**UI Binding**

- Insert the scorecard between completed scenario output and existing observability panels.
  [`app.py:69`](../../Content_MultiAgent/app.py#L69)

**Verification**

- Prove BP, LP, GP and pre-decision builder behavior from persisted artifacts.
  [`test_demo_observability.py:157`](../../Content_MultiAgent/tests/test_demo_observability.py#L157)

- Verify visible Streamlit outcomes and persistence through rerender.
  [`test_app_shell.py:44`](../../Content_MultiAgent/tests/test_app_shell.py#L44)

**Interview Surface**

- Direct the first product walkthrough through the scorecard evidence.
  [`README.md:10`](../../Content_MultiAgent/README.md#L10)

- Explain the scorecard talking points across all three scenarios.
  [`demo-script.md:8`](../../Content_MultiAgent/docs/demo-script.md#L8)
