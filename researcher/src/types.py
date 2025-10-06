from __future__ import annotations


from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, StringConstraints, constr


class Criterion(BaseModel):
    description: Annotated[str, StringConstraints(min_length=1)]


class SearchInput(BaseModel):
    query: Annotated[str, StringConstraints(min_length=1)]
    criteria: Annotated[
        list[Criterion],
        Field(
            default_factory=list,
            description="Signals that guide how the search agents evaluate relevance",
        ),
    ]
    max_count: Annotated[int, Field(..., strict=True, gt=1)]


class Investor(BaseModel):
    name: Annotated[str, Field(description="The name of the investor")]
    website: Annotated[Optional[str], Field(description="The website of the investor")]


FundingRound = Literal[
    "pre-seed", "seed", "series-a", "series-b", "series-c", "series-d", "series-e", "series-f"
]


class FundingAmount(BaseModel):
    as_reported: Annotated[str, Field(..., description="The amount of funding as reported no conversion or parenthesis")]
    value: Annotated[
        Optional[Decimal],
        Field(default=None, description="The numeric value of the funding, full digit integer"),
    ]
    currency: Annotated[
        Optional[str],
        StringConstraints(to_upper=True),
        Field(default=None, description="The ISO 4217 currency code of the funding"),
    ]


class SourceDocument(BaseModel):
    url: Optional[str]
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
    country: Optional[
        Annotated[
            str,
            StringConstraints(min_length=1),
            Field(default=None, description="The main location of the company"),
        ]
    ]


class Company(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    website: Optional[str]
    location: CompanyLocationDetails
    industry: Optional[
        Annotated[
            str,
            StringConstraints(min_length=1),
            Field(default=None, description="The industry of the company"),
        ]
    ]
    owners: Optional[
        Annotated[
            list[str],
            StringConstraints(min_length=1),
            Field(default=None, description="The owners of the company"),
        ]
    ]
    num_employees: Optional[
        Annotated[
            int,
            Field(strict=True, gt=0),
            Field(default=None, description="The number of employees of the company"),
        ]
    ]
    brief: Optional[
        Annotated[
            str,
            constr(max_length=1000),
            Field(
                default=None,
                description="The brief description of the value proposition of the company",
            ),
        ]
    ]


class CompanyFundingDigest(BaseModel):
    company: Company
    funding_events: list[FundingEvent]
    related_links: Annotated[
        list[SourceDocument],
        Field(default_factory=list, description="The related links of the company"),
    ]
    satisfies_search_criteria: Annotated[
        Literal["yes", "no", "unknown"],
        Field(default="unknown", description="Whether the company satisfies the search criteria"),
    ]


class CompanyFundingSearchResults(BaseModel):
    company_funding_digests: list[CompanyFundingDigest]
    summary: str


class StartupFundingSearchEngineOutput(BaseModel):
    search: SearchInput
    output: Annotated[CompanyFundingSearchResults, Field(description="The results of the search")]
