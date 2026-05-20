---
title: "SEO Content Multi-Agent Pipeline Addendum"
status: "draft"
created: "2026-05-19"
updated: "2026-05-19"
source: "/Users/irinawork/Downloads/SEO Content Multi-Agent Pipeline.docx"
---

# Addendum: Agent Workflow Details

## Agents

1. Orchestrator Agent
   - управляет процессом;
   - передает задачу между агентами;
   - отслеживает статусы и revision loop.

2. SEO Brief Agent
   - создает SEO-бриф из сухого входного текста;
   - определяет article type, тему, цель, audience, main keyword, secondary keywords, LSI, структуру, tone of voice и ограничения.

3. Brief QA Agent
   - проверяет, достаточно ли бриф полный для генерации текста;
   - возвращает бриф на доработку, если не хватает структуры, ключей, цели, audience или ограничений.

4. Copywriter Agent
   - пишет English US article по утвержденному брифу;
   - целевой объем: 1500-1600 слов.

5. Rewriter / Editor Agent
   - проверяет соответствие ТЗ;
   - улучшает структуру, логику и readability;
   - убирает воду;
   - проверяет, что текст не добавляет неподтвержденные факты.

6. SEO QA Agent
   - проверяет main keyword, secondary keywords, LSI, headings, word count, intent, over-optimization и соответствие типу статьи.

7. Uniqueness QA Agent
   - не симулирует uniqueness;
   - принимает score из внешнего checker/API или manual input;
   - пропускает дальше при score >= 90%;
   - возвращает на rewrite при score < 90%.

8. Spanish Localizer Agent
   - переводит и адаптирует approved English original на Spanish под выбранное гео.

9. Italian Localizer Agent
   - переводит и адаптирует approved English original на Italian.

10. French Localizer Agent
   - переводит и адаптирует approved English original на French.

11. Final QA Agent
   - проверяет финальный пакет;
   - подтверждает наличие English original, Spanish, Italian, French, QA report и uniqueness result;
   - выставляет final status: Approved или Needs Revision.

## Statuses

- Input Received
- Brief Drafted
- Brief Approved
- Writing
- Editorial Review
- SEO QA
- Uniqueness Check
- Localization
- Final QA
- Approved
- Needs Revision

## Main Workflow

```text
Input Text
-> SEO Brief Agent
-> Brief QA Agent
-> Copywriter Agent
-> Rewriter / Editor Agent
-> SEO QA Agent
-> Uniqueness QA Agent
-> Spanish / Italian / French Localizers
-> Final QA Agent
-> Final Content Package
```

## Revision Loop Rules

- проблема в брифе -> назад к SEO Brief Agent;
- проблема в тексте -> назад к Copywriter Agent;
- проблема в стиле или структуре -> назад к Rewriter Agent;
- проблема в SEO -> назад к SEO QA + Rewriter;
- uniqueness ниже 90% -> назад к Rewriter Agent;
- проблема в переводе -> назад к нужному Localizer Agent.

## Final Output Package

Финальный результат должен включать:

1. SEO brief.
2. Final English US text.
3. Spanish translation.
4. Italian translation.
5. French translation.
6. SEO QA report.
7. Uniqueness report.
8. Final status: Approved / Needs Revision.

## Honest Uniqueness Statement

Recommended product wording:

> Uniqueness validation is handled through external plagiarism checker API or manual score input. The system does not fake uniqueness scores.

## Demo Cases

1. BP Demo: сухой текст -> информационная статья.
2. LP Demo: сухой текст -> коммерческий лендинг.
3. GP Demo: сухой текст -> guest post с нативным link placement.
