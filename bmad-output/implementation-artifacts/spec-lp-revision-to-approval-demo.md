---
title: 'Demonstrate LP Revision Through Approval'
type: 'feature'
created: '2026-05-25'
status: 'done'
baseline_commit: '015d0fd5f0d9106a5a5633c23bfa98373c00121e'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/demo-script.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent - do not modify unless human renegotiates">

## Intent

**Problem:** LP демонстрация сейчас честно останавливается со статусом `needs_revision`, но оператор не может применить рекомендацию и показать завершение того же job. Для портфолио это показывает обнаружение ошибки, но не показывает управляемый цикл исправления.

**Approach:** Добавить в Streamlit управляемый action только для LP revision path: сохранить первоначальное failed QA-решение как revision history, заменить problematic draft на детерминированно исправленный текст без неподтвержденного claim и продолжить существующие gates до `approved`.

## Boundaries & Constraints

**Always:** Оставить исходный LP-run неизменным до явного действия пользователя; продолжать тот же `job_id`; сохранять evidence первоначального отказа в типизированном persisted artifact; считать итоговый approval только через существующие QA, uniqueness, localization, exporter и final QA services; показывать resolved revision в UI рядом с итоговым scorecard.

**Ask First:** Поддержка свободного редактирования текста пользователем, повторных revision loops для произвольных stages, версия каждого Markdown artifact или изменение правил GP human review.

**Never:** Не превращать LP в автоматический happy path при первом запуске; не терять failed QA evidence при перезаписи текущего editorial report; не обходить существующие quality gates; не обещать полноценный production editor/history browser.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| LP first run | LP job после `Run demo scenario` | Остается `needs_revision`; доступен action исправления; final package отсутствует | N/A |
| LP correction | LP job на editorial `needs_revision` | Failed QA сохраняется в revision history; новый draft не содержит `70 percent`; тот же job завершается `approved` с final package | N/A |
| Invalid correction request | BP/GP job либо LP не в `needs_revision` | Продолжение не запускается и existing artifacts не меняются | Показать controlled action-needed message |
| Approved after correction | LP job с финальным report и history | Scorecard показывает approval и отдельно resolved prior revision evidence | N/A |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/services/demo_pipeline_service.py` -- текущий offline orchestrator; добавит LP continuation, не меняя первый исход.
- `src/seo_content_pipeline/services/writer_service.py` -- generation boundary; должен поддержать targeted writing revision из routed editorial state.
- `src/seo_content_pipeline/models/artifacts.py`, `models/` -- registry и типизированный контракт нового `revision_history.json`.
- `src/seo_content_pipeline/ui/qa_scorecard.py`, `app.py` -- outcome presentation и explicit revision action.
- `tests/test_demo_pipeline_service.py`, `tests/test_demo_observability.py`, `tests/test_app_shell.py` -- service/UI behavior и invalid-state guards.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/models/`, `src/seo_content_pipeline/models/artifacts.py` -- определить типизированный revision history artifact и зарегистрировать его для просмотра/download.
- [x] `src/seo_content_pipeline/services/writer_service.py`, `src/seo_content_pipeline/services/demo_pipeline_service.py` -- реализовать targeted LP revision continuation с сохранением failed QA и обычным прохождением remaining gates.
- [x] `src/seo_content_pipeline/ui/qa_scorecard.py`, `app.py` -- показать action на LP failure и resolved history после успешного продолжения.
- [x] `tests/` -- проверить первый stop, correction-to-approval, history persistence, rejected invalid action и Streamlit interaction.
- [x] `README.md`, `docs/demo-script.md`, `docs/interview-cheatsheet.md`, `docs/roadmap.md` -- описать новый interview workflow и честный оставшийся scope.

**Acceptance Criteria:**
- Given LP initially routed for an unsupported claim, when оператор еще не выбрал correction action, then status остается `needs_revision`, current draft/report показывают проблему и final package не существует.
- Given routed LP, when оператор запускает correction action, then тот же job сохраняет structured revision history, создает corrected draft без `70 percent`, проходит normal gates и завершается `approved`.
- Given BP, GP or already-approved job, when correction continuation вызвана ошибочно, then service rejects it with a controlled UI-facing error and does not claim a revision occurred.
- Given corrected LP is approved, when оператор смотрит scorecard/artifacts, then видны final approval, final package и resolved evidence первоначального editorial failure.

## Spec Change Log

## Design Notes

`revision_history.json` сохраняет structured failed decision и рекомендацию до перезаписи текущих working artifacts. Это обеспечивает audit trail для demo без внедрения полноценного versioned document editor. Сценарий GP остается ручной остановкой: автоматическое принятие решения о публикационной ссылке противоречило бы смыслу human-review path.

## Verification

**Commands:**
- `uv run ruff check .` -- expected: lint passes.
- `uv run pytest tests/test_demo_pipeline_service.py tests/test_demo_observability.py tests/test_app_shell.py` -- expected: revision lifecycle and UI pass.
- `make --no-print-directory release-check` -- expected: regression gate passes; initial BP/LP/GP outcomes stay distinct.

## Suggested Review Order

**Continuation Flow**

- Continue only a routed LP failure through the established downstream gates.
  [`demo_pipeline_service.py:122`](../../Content_MultiAgent/src/seo_content_pipeline/services/demo_pipeline_service.py#L122)

- Re-enter writing through a validated editorial routing boundary.
  [`writer_service.py:71`](../../Content_MultiAgent/src/seo_content_pipeline/services/writer_service.py#L71)

**Decision Evidence**

- Preserve failed QA before working artifacts are replaced.
  [`demo_pipeline_service.py:185`](../../Content_MultiAgent/src/seo_content_pipeline/services/demo_pipeline_service.py#L185)

- Model the revision audit entry as a persisted typed artifact.
  [`revision.py:11`](../../Content_MultiAgent/src/seo_content_pipeline/models/revision.py#L11)

**User Interaction**

- Expose one explicit correction action and rerender the approved result.
  [`app.py:74`](../../Content_MultiAgent/app.py#L74)

- Present resolved failure evidence beside the final decision scorecard.
  [`qa_scorecard.py:64`](../../Content_MultiAgent/src/seo_content_pipeline/ui/qa_scorecard.py#L64)

**Verification And Demo**

- Cover both writing modes, invalid routes and repeat-application rejection.
  [`test_demo_pipeline_service.py:125`](../../Content_MultiAgent/tests/test_demo_pipeline_service.py#L125)

- Exercise the operator action through the Streamlit interface.
  [`test_app_shell.py:44`](../../Content_MultiAgent/tests/test_app_shell.py#L44)

- Explain the correction-to-approval narrative used in the portfolio demo.
  [`demo-script.md:11`](../../Content_MultiAgent/docs/demo-script.md#L11)
