from __future__ import annotations


from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, StringConstraints, constr, field_validator
from pydantic.networks import AnyHttpUrl

from src.utils.currency import CURRENCY_CODES

class Criterion(BaseModel):
    description: Annotated[str, StringConstraints(min_length=1)]


class Search(BaseModel):
    query: Annotated[str, StringConstraints(min_length=1)]
    criteria: Annotated[list[Criterion], Field(default_factory=list, description="Signals that guide how the search agents evaluate relevance")]
    relevant_count: Annotated[int, Field(..., strict=True, gt=0)]
    max_count: Annotated[int, Field(..., strict=True, gt=1)]


class Investor(BaseModel):
    name: Annotated[str, Field(description="The name of the investor")]
    website: Annotated[Optional[str], Field(description="The website of the investor")]


FundingRound = Literal["pre-seed", "seed", "series-a", "series-b", "series-c", "series-d", "series-e", "series-f"]


class FundingAmount(BaseModel):
    as_reported: Annotated[str, Field(..., description="The amount of funding as reported")]
    value: Annotated[Optional[Decimal], Field(default=None, description="The numeric value of the funding when available")]
    currency: Annotated[Optional[str], StringConstraints(to_upper=True), Field(default=None, description="The ISO 4217 currency code of the funding")]

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in CURRENCY_CODES:
            raise ValueError(f"Unsupported currency code: {value}")
        return value


class SourceDocument(BaseModel):
    url: AnyHttpUrl
    title: Optional[str]
    publisher: Optional[str]
    published_at: Optional[datetime]
    snippet: Optional[str]


class FundingEvent(BaseModel):
    round: FundingRound
    announced_date: date
    amount: FundingAmount
    investors: list[Investor] = Field(default_factory=list)
    lead_investor: Optional[Investor] = None
    source_documents: list[SourceDocument]


class CompanyLocationDetails(BaseModel):
    country: Optional[Annotated[str, StringConstraints(min_length=1)]]
    headquarters_city: Optional[Annotated[str, StringConstraints(min_length=1)]]
    headquarters_state: Optional[Annotated[str, StringConstraints(min_length=1)]]
    headquarters_zip_code: Optional[Annotated[str, StringConstraints(min_length=1)]]
    headquarters_address: Optional[Annotated[str, StringConstraints(min_length=1)]]


class Company(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    website: Optional[AnyHttpUrl]
    location: CompanyLocationDetails
    industry: Optional[Annotated[str, StringConstraints(min_length=1)]]
    owners: Optional[Annotated[list[str], StringConstraints(min_length=1)]]
    employees: Optional[Annotated[int, Field(strict=True, gt=0)]]
    brief: Optional[Annotated[str, constr(max_length=1000)]]


class CompanyFundingDigest(BaseModel):
    company: Company
    funding_events: list[FundingEvent]
    related_links: Annotated[list[SourceDocument], Field(default_factory=list, description="The related links of the company")]


class CompanyFundingSearchResults(BaseModel):
    company_funding_digests: list[CompanyFundingDigest]
    summary: str


class StartupFundingSearchEngineOutput(BaseModel):
    search: Search
    output: Annotated[CompanyFundingSearchResults, Field(description="The results of the search")]