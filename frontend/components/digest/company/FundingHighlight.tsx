import type { FundingEvent } from "@/lib/getDigest";

interface FundingHighlightProps {
  amount: string;
  roundLabel?: string;
  announced?: string | null;
  investors: FundingEvent["investors"];
  leadInvestor?: FundingEvent["lead_investor"] | null;
}

export function FundingHighlight({ amount, roundLabel, announced, investors, leadInvestor }: FundingHighlightProps) {
  const investorList = investors ?? [];

  return (
    <section className="w-full flex flex-col">
      <p className="text-xs uppercase tracking-[0.16em] text-foreground/60 leading-none">Round size</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight sm:text-[2rem]">{amount}</p>
      {roundLabel && <p className="mt-1 text-sm text-foreground/70">{roundLabel}</p>}
      {announced && <p className="mt-2 text-xs text-foreground/60">Announced {announced}</p>}

      <div className="mt-8 space-y-3">
        <p className="text-xs uppercase tracking-[0.14em] text-foreground/60 font-normal">
          Investors {investorList.length ? `(${investorList.length})` : ""}
        </p>
        {investorList.length > 0 ? (
          <div className="space-y-3 text-sm text-foreground/80">
            {investorList.map((investor, index) => {
              const label = investor.name || investor.website || "Investor";
              const isLead = Boolean(leadInvestor?.name && investor.name === leadInvestor.name);
              return (
                <div key={`${label}-${index}`} className="flex flex-wrap items-center gap-2">
                  {investor.website ? (
                    <a
                      href={investor.website}
                      target="_blank"
                      rel="noreferrer"
                      className="underline decoration-foreground/30 underline-offset-4 transition hover:decoration-foreground hover:text-foreground"
                    >
                      {label}
                    </a>
                  ) : (
                    <span>{label}</span>
                  )}
                  {isLead && (
                    <span className="rounded bg-muted/60 px-1.5 py-0.5 text-[0.65rem] uppercase tracking-[0.12em] text-foreground/70">
                      Lead
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-foreground/70">—</p>
        )}
      </div>
    </section>
  );
}
