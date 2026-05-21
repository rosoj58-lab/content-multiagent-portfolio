"""Content artifact contracts."""

from pydantic import BaseModel, Field

from seo_content_pipeline.models.job import ArticleType
from seo_content_pipeline.models.stage import WorkflowStage


class BriefOutlineSection(BaseModel):
    """One H2 section with supporting H3 subsections."""

    h2: str = Field(min_length=1)
    h3: list[str] = Field(min_length=1)


class BriefOutline(BaseModel):
    """H1/H2/H3 article outline for the SEO brief."""

    h1: str = Field(min_length=1)
    sections: list[BriefOutlineSection] = Field(min_length=1)


class SEOBrief(BaseModel):
    """Structured SEO brief generated from dry input."""

    topic: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    main_keyword: str = Field(min_length=1)
    secondary_keywords: list[str] = Field(min_length=1)
    lsi_keywords: list[str] = Field(min_length=1)
    outline: BriefOutline
    tone_of_voice: str = Field(min_length=1)
    constraints: list[str] = Field(min_length=1)


class SEOBriefArtifact(BaseModel):
    """Persisted SEO brief artifact with workflow context."""

    job_id: str
    stage: WorkflowStage = WorkflowStage.BRIEF_DRAFTED
    article_type: ArticleType
    brief: SEOBrief
