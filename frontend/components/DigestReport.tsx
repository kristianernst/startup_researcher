"use client";

import type { DigestRoot } from "@/lib/getDigest";
import {
  CompanyDigestCard,
  DigestHeader,
  DigestStats,
  computeStats,
  formatCurrencyShort,
  getMonthLabel,
} from "./digest";
import type { CompanyDigest, FundingEvent } from "./digest";

interface DigestReportProps {
  data: DigestRoot;
}

export function DigestReport({ data }: DigestReportProps) {
  const digests = data.company_funding_digests || [];
  const monthLabel = getMonthLabel(digests);
  const stats = computeStats(digests);
  const hasDeals = digests.length > 0;

  const totalDisplay = hasDeals ? formatCurrencyShort(stats.total, stats.currency || undefined) : "—";
  const medianDisplay = hasDeals ? formatCurrencyShort(stats.median, stats.currency || undefined) : "—";
  const largestValue = Number.isFinite(stats.largest.numeric) ? stats.largest.numeric : null;
  const largestDisplay = largestValue !== null ? formatCurrencyShort(largestValue, stats.currency || undefined) : "—";
  const largestSubtitle = stats.largest.event
    ? [stats.largest.event.round?.toUpperCase() || "", stats.largest.company?.company.name || ""]
        .filter(Boolean)
        .join(" — ") || undefined
    : undefined;
  const rounds = buildRoundPills(stats);

  return (
    <main className="mx-auto max-w-7xl px-5 py-12 sm:px-6 md:px-8 lg:px-12">
      <DigestHeader monthLabel={monthLabel} summary={data.summary} />

      <DigestStats
        dealsCount={digests.length}
        totalRaised={totalDisplay}
        totalSubtitle={hasDeals ? stats.currency || undefined : undefined}
        medianRound={medianDisplay}
        largestRound={largestDisplay}
        largestSubtitle={largestSubtitle}
        rounds={rounds}
        topInvestor={stats.topInvestor ? { name: stats.topInvestor[0], count: stats.topInvestor[1] } : null}
      />

      <section aria-labelledby="deals" className="space-y-6">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <h2 id="deals" className="text-2xl font-semibold tracking-tight sm:text-3xl" style={{ fontFamily: "var(--font-body)" }}>
            Funding rounds
          </h2>
          {hasDeals && (
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground/70">
              {digests.length} {digests.length === 1 ? "company" : "companies"}
            </p>
          )}
        </div>

        {!hasDeals ? (
          <p className="rounded-xl border border-border/70 bg-muted/30 px-6 py-8 text-sm text-muted-foreground">
            We didn&apos;t find any funding announcements that matched the criteria for this period. Try widening your filters or run a fresh research job.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-8 md:gap-10">
            {digests.map((digest, index) => (
              <CompanyDigestCard key={`${digest.company.name}-${index}`} digest={digest} />
            ))}
          </div>
        )}
      </section>

      <footer className="mt-12 text-xs text-muted-foreground">
        Automatically compiled with an AI research agent. Hallucinations are possible. Developed by
        {" "}
        <a
          href="https://kristian-ernst.netlify.app"
          className="underline decoration-transparent transition hover:decoration-foreground/60"
        >
          Kristian Ernst
        </a>
        .
      </footer>
    </main>
  );
}

function buildRoundPills(stats: ReturnType<typeof computeStats>) {
  const roundOrder = [
    "pre-seed",
    "seed",
    "series-a",
    "series-b",
    "series-c",
    "series-d",
    "grant",
    "debt",
    "unknown",
  ] as const;

  return roundOrder
    .filter((round) => stats.byRound[round] && stats.byRound[round] > 0)
    .map((round) => ({
      key: round,
      label: `Rounds: ${round.replace("-", " ")}`,
      value: String(stats.byRound[round]),
    }));
}

export type { CompanyDigest, DigestRoot, FundingEvent };
