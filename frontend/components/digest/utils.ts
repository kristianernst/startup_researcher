import type { CompanyDigest, FundingEvent } from "@/lib/getDigest";

export function formatCurrencyShort(value: number, currency: string = "EUR"): string {
  if (!Number.isFinite(value)) return "—";
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  const symbol = currency === "EUR" ? "€" : currency === "USD" ? "$" : "";
  if (abs >= 1_000_000_000) return `${sign}${symbol}${(abs / 1_000_000_000).toFixed(1)}B`;
  if (abs >= 1_000_000) return `${sign}${symbol}${(abs / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000) return `${sign}${symbol}${(abs / 1_000).toFixed(1)}K`;
  return `${sign}${symbol}${abs.toLocaleString()}`;
}

export function formatDate(d: string | null | undefined): string {
  if (!d) return "—";
  const dt = new Date(d);
  if (Number.isNaN(dt.getTime())) return d;
  return dt.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "2-digit" });
}

export function getMonthLabel(digests: CompanyDigest[]): string | null {
  const months = new Set(
    digests
      .flatMap((cd) => cd.funding_events?.map((fe) => fe.announced_date).filter(Boolean) || [])
      .map((date) => {
        const dt = new Date(date as string);
        if (Number.isNaN(dt.getTime())) return null;
        return `${dt.toLocaleString(undefined, { month: "long" })} ${dt.getFullYear()}`;
      })
      .filter(Boolean) as string[]
  );
  if (months.size === 1) return Array.from(months)[0] as string;
  if (months.size > 1) return `${Array.from(months).join(" – ")}`;
  return null;
}

export function amountToNumber(value: number | string | null | undefined): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number(value.replace(/[^0-9.\-]+/g, ""));
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

export function computeStats(digests: CompanyDigest[]) {
  const events = digests.flatMap((d) => d.funding_events || []);
  const amounts = events
    .map((e) => amountToNumber(e.amount?.value))
    .filter((n): n is number => typeof n === "number" && !Number.isNaN(n));
  const currency = events.find((e) => e.amount?.currency)?.amount?.currency ?? undefined;
  const total = amounts.reduce((a, b) => a + b, 0);
  const sorted = [...amounts].sort((a, b) => a - b);
  const median = sorted.length
    ? sorted.length % 2
      ? sorted[(sorted.length - 1) / 2]
      : (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
    : 0;

  const largest = events.reduce<{
    event: FundingEvent | null;
    company: CompanyDigest | null;
    numeric: number;
  }>((acc, e) => {
    const numeric = amountToNumber(e.amount?.value) ?? -Infinity;
    if (!acc.event || numeric > acc.numeric) {
      const company = digests.find((d) => d.funding_events.includes(e)) || null;
      return { event: e, company, numeric };
    }
    return acc;
  }, { event: null, company: null, numeric: -Infinity });

  const byRound = events.reduce<Record<string, number>>((acc, e) => {
    const key = (e.round || "unknown").toLowerCase();
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  const investorCounts = events.reduce<Record<string, number>>((acc, e) => {
    (e.investors || []).forEach((i) => {
      const key = i.name?.trim();
      if (!key) return;
      acc[key] = (acc[key] || 0) + 1;
    });
    return acc;
  }, {});
  const topInvestor = Object.entries(investorCounts).sort((a, b) => b[1] - a[1])[0] || null;

  return { total, median, currency, largest, byRound, topInvestor };
}

export type { CompanyDigest, FundingEvent };
