import type { CompanyDigest, FundingEvent, SourceDocument } from "@/lib/getDigest";
import { amountToNumber, formatCurrencyShort, formatDate } from "../utils";
import { CompanyHeader } from "./CompanyHeader";
import { FundingHighlight } from "./FundingHighlight";
import { CompanySnapshot } from "./CompanySnapshot";

interface CompanyDigestCardProps {
  digest: CompanyDigest;
}

export function CompanyDigestCard({ digest }: CompanyDigestCardProps) {
  const events = digest.funding_events || [];
  const sources = collectSources(events);
  const firstEvent = events[0] || null;
  const numericValues = events
    .map((event) => amountToNumber(event.amount?.value))
    .filter((value): value is number => typeof value === "number" && !Number.isNaN(value));
  const hasMultipleRounds = events.length > 1 && numericValues.length > 0;
  const sumValue = hasMultipleRounds ? numericValues.reduce((acc, value) => acc + value, 0) : null;
  const sumCurrency = hasMultipleRounds
    ? events.find((event) => event.amount?.currency)?.amount?.currency ?? undefined
    : undefined;

  const highlightAmount = computeHighlightAmount({ hasMultipleRounds, sumValue, sumCurrency, firstEvent });
  const roundLabel = hasMultipleRounds
    ? `${events.length} rounds`
    : firstEvent?.round?.toUpperCase() || undefined;
  const highlightAnnounced = firstEvent?.announced_date ? formatDate(firstEvent.announced_date) : null;

  return (
    <article className="rounded-3xl bg-card/95 p-6 sm:p-8 lg:p-10">
      <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-[1fr_auto] lg:gap-16">
        <div className="space-y-10">
          <CompanyHeader company={digest.company} sources={sources} />
          <CompanySnapshot company={digest.company} />
        </div>
        
        <div className="lg:min-w-[280px] xl:min-w-[320px]">
          <FundingHighlight
            amount={highlightAmount}
            roundLabel={roundLabel}
            announced={highlightAnnounced}
            investors={firstEvent?.investors ?? []}
            leadInvestor={firstEvent?.lead_investor ?? null}
          />
        </div>
      </div>
    </article>
  );
}

function collectSources(events: FundingEvent[]): SourceDocument[] {
  return events.flatMap((event) => event.source_documents || []).filter((source): source is SourceDocument => Boolean(source));
}

function computeHighlightAmount({
  hasMultipleRounds,
  sumValue,
  sumCurrency,
  firstEvent,
}: {
  hasMultipleRounds: boolean;
  sumValue: number | null;
  sumCurrency: string | undefined;
  firstEvent: FundingEvent | null;
}): string {
  if (hasMultipleRounds && sumValue !== null) {
    return formatCurrencyShort(sumValue, sumCurrency);
  }
  if (firstEvent) {
    const numeric = amountToNumber(firstEvent.amount?.value);
    if (numeric !== null) {
      return formatCurrencyShort(numeric, firstEvent.amount?.currency || undefined);
    }
    if (firstEvent.amount?.as_reported) {
      return firstEvent.amount.as_reported;
    }
  }
  return "—";
}
