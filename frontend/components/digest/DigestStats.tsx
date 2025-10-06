interface DigestStatsProps {
  dealsCount: number;
  totalRaised: string;
  totalSubtitle?: string;
  medianRound: string;
  largestRound: string;
  largestSubtitle?: string;
  rounds: Array<{ key: string; label: string; value: string }>;
  topInvestor?: { name: string; count: number } | null;
}

export function DigestStats({
  dealsCount,
  totalRaised,
  totalSubtitle,
  medianRound,
  largestRound,
  largestSubtitle,
  rounds,
  topInvestor,
}: DigestStatsProps) {
  return (
    <section aria-labelledby="key-numbers" className="mb-12 space-y-6">
      <h2 id="key-numbers" className="sr-only">
        Key numbers
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Deals tracked" value={String(dealsCount)} subtitle="companies with announced rounds" />
        <StatCard label="Total raised" value={totalRaised} subtitle={totalSubtitle} />
        <StatCard label="Median round" value={medianRound} />
        <StatCard label="Largest round" value={largestRound} subtitle={largestSubtitle} />
      </div>

      <div className="flex flex-wrap gap-2">
        {rounds.map((round) => (
          <StatPill key={round.key} label={round.label} value={round.value} />
        ))}
        {topInvestor && (
          <StatPill label="Top mentioned investor" value={`${topInvestor.name} (${topInvestor.count})`} />
        )}
      </div>
    </section>
  );
}

function StatCard({ label, value, subtitle }: { label: string; value: string; subtitle?: string }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-card/80 p-5 shadow-sm">
      <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-3 text-2xl font-semibold tracking-tight sm:text-[1.9rem]">{value}</p>
      {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
    </div>
  );
}

function StatPill({ label, value }: { label: string; value: string }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-muted/40 px-3.5 py-1.5 text-xs text-muted-foreground">
      <span>{label}</span>
      <span className="font-medium text-foreground">{value}</span>
    </span>
  );
}
