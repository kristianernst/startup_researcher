"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { DigestReport, type CompanyDigest, type DigestRoot, type FundingEvent } from "@/components/DigestReport";

interface DigestRecordResponse {
  run_id: string | null;
  created_at: string | null;
  data: DigestRoot;
}

function createEmptyCompanyDigest(): CompanyDigest {
  return {
    company: {
      name: "",
      website: null,
      location: { country: null },
      industry: null,
      owners: null,
      num_employees: null,
      brief: null,
    },
    funding_events: [],
    related_links: [],
    satisfies_search_criteria: null,
  };
}

interface ApiState {
  loading: boolean;
  error: string | null;
  saving: boolean;
  savedAt: number | null;
}

export default function AdminPage() {
  const [draft, setDraft] = useState<DigestRoot | null>(null);
  const [original, setOriginal] = useState<DigestRoot | null>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [{ loading, error, saving, savedAt }, setApiState] = useState<ApiState>({
    loading: true,
    error: null,
    saving: false,
    savedAt: null,
  });

  useEffect(() => {
    let cancelled = false;
    async function loadDigest() {
      setApiState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const response = await fetch("/api/digest", { cache: "no-store" });
        if (!response.ok) throw new Error(`Failed with ${response.status}`);
        const payload = (await response.json()) as DigestRecordResponse;
        const data = payload?.data ?? { company_funding_digests: [], summary: "No data to display yet." };
        if (cancelled) return;
        setDraft(data);
        setOriginal(data);
        setRunId(payload?.run_id ?? null);
        setApiState({
          loading: false,
          error: null,
          saving: false,
          savedAt: payload?.created_at ? new Date(payload.created_at).getTime() : null,
        });
      } catch (err) {
        if (cancelled) return;
        setApiState((prev) => ({ ...prev, loading: false, error: (err as Error).message }));
      }
    }

    loadDigest();
    return () => {
      cancelled = true;
    };
  }, []);

  const originalString = useMemo(() => (original ? JSON.stringify(original) : null), [original]);
  const draftString = useMemo(() => (draft ? JSON.stringify(draft) : null), [draft]);
  const hasChanges = Boolean(draft && original && originalString !== draftString);

  const mutateCompany = useCallback(
    (companyIndex: number, updater: (company: CompanyDigest) => CompanyDigest) => {
      setDraft((prev) => {
        if (!prev) return prev;
        const nextCompanies = prev.company_funding_digests.map((company, idx) =>
          idx === companyIndex ? updater(company) : company
        );
        return { ...prev, company_funding_digests: nextCompanies };
      });
    },
    []
  );

  const mutateEvent = useCallback(
    (companyIndex: number, eventIndex: number, updater: (event: FundingEvent) => FundingEvent) => {
      mutateCompany(companyIndex, (company) => {
        const nextEvents = company.funding_events.map((event, idx) =>
          idx === eventIndex ? updater(event) : event
        );
        return { ...company, funding_events: nextEvents };
      });
    },
    [mutateCompany]
  );

  const handleSummaryChange = useCallback((value: string) => {
    setDraft((prev) => (prev ? { ...prev, summary: value } : prev));
  }, []);

  const handleAddCompany = useCallback(() => {
    setDraft((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        company_funding_digests: [...prev.company_funding_digests, createEmptyCompanyDigest()],
      };
    });
  }, []);

  const handleRemoveCompany = useCallback((companyIndex: number) => {
    setDraft((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        company_funding_digests: prev.company_funding_digests.filter((_, idx) => idx !== companyIndex),
      };
    });
  }, []);

  const handleSave = useCallback(async () => {
    if (!draft) return;
    setApiState((prev) => ({ ...prev, saving: true, error: null }));
    try {
      const response = await fetch("/api/digest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: draft, run_id: runId ?? undefined }),
      });
      if (!response.ok) throw new Error(`Failed with ${response.status}`);
      const payload = (await response.json()) as DigestRecordResponse;
      const saved = payload?.data ?? draft;
      setOriginal(saved);
      setDraft(saved);
      setRunId(payload?.run_id ?? null);
      setApiState({
        loading: false,
        error: null,
        saving: false,
        savedAt: payload?.created_at ? new Date(payload.created_at).getTime() : Date.now(),
      });
    } catch (err) {
      setApiState((prev) => ({ ...prev, saving: false, error: (err as Error).message }));
    }
  }, [draft, runId]);

  if (loading) {
    return (
      <main className="mx-auto max-w-6xl px-5 sm:px-6 md:px-8 py-12">
        <h1 className="text-2xl font-semibold">Admin</h1>
        <p className="mt-6 text-sm text-muted-foreground">Loading digest…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="mx-auto max-w-6xl px-5 sm:px-6 md:px-8 py-12">
        <h1 className="text-2xl font-semibold">Admin</h1>
        <p className="mt-6 text-sm text-destructive">{error}</p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="mt-4 inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Retry
        </button>
      </main>
    );
  }

  if (!draft) {
    return null;
  }

  return (
    <main className="mx-auto max-w-6xl px-5 sm:px-6 md:px-8 py-12">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Admin editor</h1>
          <p className="text-sm text-muted-foreground">Tweak digest copy and instantly preview the report.</p>
        </div>
        <div className="flex items-center gap-3">
          {savedAt && (
            <span className="text-xs text-muted-foreground">
              Saved {new Date(savedAt).toLocaleTimeString()}
            </span>
          )}
          <button
            type="button"
            onClick={handleSave}
            disabled={!hasChanges || saving}
            className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition disabled:cursor-not-allowed disabled:opacity-60"
          >
            {saving ? "Saving…" : hasChanges ? "Save changes" : "Saved"}
          </button>
        </div>
      </div>

      <div className="mt-10 grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,28rem)] lg:items-start">
        <div className="space-y-8">
          <section className="rounded-xl border bg-card/40 p-6">
            <h2 className="text-lg font-semibold">Summary</h2>
            <p className="mt-1 text-xs text-muted-foreground">This copy appears at the top of the digest.</p>
            <textarea
              value={draft.summary ?? ""}
              onChange={(event) => handleSummaryChange(event.target.value)}
              rows={4}
              className="mt-4 w-full rounded-lg border bg-background px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="Add a short narrative for the month…"
            />
          </section>

          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">Companies</h2>
            <button
              type="button"
              onClick={handleAddCompany}
              className="inline-flex items-center gap-2 rounded-md border border-dashed border-primary/60 px-3 py-2 text-xs font-medium text-primary hover:border-primary hover:bg-primary/10"
            >
              Add company
            </button>
          </div>

          {draft.company_funding_digests.length === 0 && (
            <p className="rounded-md border border-dashed bg-muted/40 p-4 text-xs text-muted-foreground">
              No companies yet. Add one to begin composing this month’s digest.
            </p>
          )}

          {draft.company_funding_digests.map((company, companyIndex) => (
            <CompanyEditor
              key={`${company.company.name || "company"}-${companyIndex}`}
              company={company}
              onChange={(updater) => mutateCompany(companyIndex, updater)}
              onEventChange={(eventIndex, updater) => mutateEvent(companyIndex, eventIndex, updater)}
              onRemove={() => handleRemoveCompany(companyIndex)}
            />
          ))}
        </div>

        <aside className="sticky top-10 h-fit rounded-xl border bg-muted/30 p-4">
          <h2 className="text-sm font-semibold text-muted-foreground">Live preview</h2>
          <div className="mt-4 max-h-[80vh] overflow-y-auto rounded-lg border bg-background">
            <DigestReport data={draft} />
          </div>
        </aside>
      </div>
    </main>
  );
}

function CompanyEditor({
  company,
  onChange,
  onEventChange,
  onRemove,
}: {
  company: CompanyDigest;
  onChange: (updater: (current: CompanyDigest) => CompanyDigest) => void;
  onEventChange: (eventIndex: number, updater: (event: FundingEvent) => FundingEvent) => void;
  onRemove?: () => void;
}) {
  const handleCompanyField = useCallback(
    (field: keyof CompanyDigest["company"], value: string) => {
      onChange((current) => ({
        ...current,
        company: { ...current.company, [field]: value },
      }));
    },
    [onChange]
  );

  const handleOwnersChange = useCallback(
    (value: string) => {
      const owners = value
        .split(",")
        .map((entry) => entry.trim())
        .filter((entry) => entry.length > 0);
      onChange((current) => ({
        ...current,
        company: { ...current.company, owners: owners.length ? owners : null },
      }));
    },
    [onChange]
  );

  const handleEmployeesChange = useCallback(
    (value: string) => {
      const trimmed = value.trim();
      const parsed = Number(trimmed);
      onChange((current) => ({
        ...current,
        company: {
          ...current.company,
          num_employees: trimmed === "" ? null : Number.isNaN(parsed) ? current.company.num_employees ?? null : parsed,
        },
      }));
    },
    [onChange]
  );

  const handleCountryChange = useCallback(
    (value: string) => {
      const trimmed = value.trim();
      onChange((current) => ({
        ...current,
        company: {
          ...current.company,
          location: {
            ...(current.company.location ?? {}),
            country: trimmed === "" ? null : trimmed,
          },
        },
      }));
    },
    [onChange]
  );

  const handleAddEvent = useCallback(() => {
    onChange((current) => ({
      ...current,
      funding_events: [
        ...current.funding_events,
        {
          round: null,
          announced_date: null,
          amount: { as_reported: null, value: null, currency: null },
          investors: [],
          lead_investor: null,
          source_documents: [],
        },
      ],
    }));
  }, [onChange]);

  const handleRemoveEvent = useCallback(
    (eventIndex: number) => {
      onChange((current) => ({
        ...current,
        funding_events: current.funding_events.filter((_, idx) => idx !== eventIndex),
      }));
    },
    [onChange]
  );

  return (
    <section className="rounded-xl border bg-card/40 p-6">
      <div className="flex flex-col gap-0.5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">{company.company.name || "Untitled company"}</h2>
          <p className="text-xs text-muted-foreground">Update company details and funding events.</p>
        </div>
        {onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="mt-2 inline-flex items-center text-xs font-medium text-destructive hover:underline sm:mt-0"
          >
            Remove company
          </button>
        )}
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Company name
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={company.company.name}
            onChange={(event) => handleCompanyField("name", event.target.value)}
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Website
          <input
            type="url"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={company.company.website ?? ""}
            onChange={(event) => handleCompanyField("website", event.target.value)}
            placeholder="https://"
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Industry
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={company.company.industry ?? ""}
            onChange={(event) => handleCompanyField("industry", event.target.value)}
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Country
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={company.company.location?.country ?? ""}
            onChange={(event) => handleCountryChange(event.target.value)}
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Founders
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={(company.company.owners ?? []).join(", ")}
            onChange={(event) => handleOwnersChange(event.target.value)}
            placeholder="Comma separated list"
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Employees
          <input
            type="number"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={company.company.num_employees ?? ""}
            onChange={(event) => handleEmployeesChange(event.target.value)}
            min={0}
          />
        </label>
      </div>

      <label className="mt-4 block space-y-1 text-xs font-medium text-muted-foreground">
        Brief
        <textarea
          className="w-full rounded-md border bg-background px-3 py-2 text-sm"
          rows={3}
          value={company.company.brief ?? ""}
          onChange={(event) => handleCompanyField("brief", event.target.value)}
          placeholder="Short description of what the company does"
        />
      </label>

      <div className="mt-6 space-y-5">
        {company.funding_events.length === 0 && (
          <p className="rounded-md border border-dashed bg-muted/40 p-4 text-xs text-muted-foreground">
            No funding events yet. Add one below to start the company timeline.
          </p>
        )}
        {company.funding_events.map((event, eventIndex) => (
          <FundingEventEditor
            key={`${event.round || "event"}-${eventIndex}`}
            event={event}
            onChange={(updater) => onEventChange(eventIndex, updater)}
            onRemove={() => handleRemoveEvent(eventIndex)}
          />
        ))}
      </div>

      <div className="mt-4">
        <button
          type="button"
          onClick={handleAddEvent}
          className="inline-flex items-center rounded-md border border-dashed border-primary/60 px-3 py-2 text-xs font-medium text-primary hover:border-primary hover:bg-primary/10"
        >
          Add funding event
        </button>
      </div>
    </section>
  );
}

function FundingEventEditor({
  event,
  onChange,
  onRemove,
}: {
  event: FundingEvent;
  onChange: (updater: (current: FundingEvent) => FundingEvent) => void;
  onRemove?: () => void;
}) {
  const handleField = useCallback(
    (field: keyof FundingEvent, value: string) => {
      onChange((current) => ({
        ...current,
        [field]: value === "" ? null : value,
      }));
    },
    [onChange]
  );

  const handleAmountField = useCallback(
    (field: "as_reported" | "value" | "currency", value: string) => {
      onChange((current) => {
        const amount = current.amount ?? { as_reported: null, value: null, currency: null };
        let nextValue: number | string | null = value;
        if (field === "value") {
          const trimmed = value.trim();
          if (trimmed === "") {
            nextValue = null;
          } else {
            const parsed = Number(trimmed);
            nextValue = Number.isNaN(parsed) ? trimmed : parsed;
          }
        } else {
          nextValue = value.trim() === "" ? null : value;
        }
        return {
          ...current,
          amount: { ...amount, [field]: nextValue },
        };
      });
    },
    [onChange]
  );

  const handleInvestorsChange = useCallback(
    (value: string) => {
      const entries = value
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line.length > 0)
        .map((line) => {
          const [name, website] = line.split("|").map((piece) => piece.trim());
          return { name, website: website || null };
        });
      onChange((current) => ({
        ...current,
        investors: entries,
      }));
    },
    [onChange]
  );

  const handleLeadInvestorChange = useCallback(
    (value: string) => {
      const trimmed = value.trim();
      onChange((current) => ({
        ...current,
        lead_investor: trimmed === "" ? null : { name: trimmed, website: null },
      }));
    },
    [onChange]
  );

  const handleAddSource = useCallback(() => {
    onChange((current) => ({
      ...current,
      source_documents: [
        ...(current.source_documents ?? []),
        { url: null, title: null, publisher: null, published_at: null, snippet: null },
      ],
    }));
  }, [onChange]);

  const handleSourceField = useCallback(
    (index: number, field: "url" | "title" | "publisher" | "published_at" | "snippet", value: string) => {
      onChange((current) => {
        const sources = [...(current.source_documents ?? [])];
        const existing = sources[index] ?? { url: null, title: null, publisher: null, published_at: null, snippet: null };
        const trimmed = field === "snippet" ? value : value.trim();
        sources[index] = {
          ...existing,
          [field]: trimmed === "" ? null : trimmed,
        };
        return { ...current, source_documents: sources };
      });
    },
    [onChange]
  );

  const handleRemoveSource = useCallback(
    (index: number) => {
      onChange((current) => {
        const nextSources = (current.source_documents ?? []).filter((_, idx) => idx !== index);
        return { ...current, source_documents: nextSources };
      });
    },
    [onChange]
  );

  return (
    <div className="rounded-lg border bg-background p-4">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold">Funding event</h3>
        {onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="text-xs font-medium text-destructive hover:underline"
          >
            Remove
          </button>
        )}
      </div>
      <div className="mt-3 grid gap-4 md:grid-cols-2">
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Round
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={event.round ?? ""}
            onChange={(event) => handleField("round", event.target.value)}
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Announced date
          <input
            type="date"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={event.announced_date ?? ""}
            onChange={(event) => handleField("announced_date", event.target.value)}
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Amount (reported)
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={event.amount?.as_reported ?? ""}
            onChange={(event) => handleAmountField("as_reported", event.target.value)}
            placeholder="€10 million"
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Amount (value)
          <input
            type="number"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={event.amount?.value ?? ""}
            onChange={(event) => handleAmountField("value", event.target.value)}
            placeholder="10000000"
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Currency
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={event.amount?.currency ?? ""}
            onChange={(event) => handleAmountField("currency", event.target.value)}
            placeholder="EUR"
          />
        </label>
        <label className="space-y-1 text-xs font-medium text-muted-foreground">
          Lead investor
          <input
            type="text"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={event.lead_investor?.name ?? ""}
            onChange={(event) => handleLeadInvestorChange(event.target.value)}
            placeholder="Investor name"
          />
        </label>
      </div>

      <label className="mt-4 block space-y-1 text-xs font-medium text-muted-foreground">
        Investors
        <textarea
          className="w-full rounded-md border bg-background px-3 py-2 text-sm"
          rows={4}
          value={(event.investors || []).map((inv) => (inv.website ? `${inv.name} | ${inv.website}` : inv.name)).join("\n")}
          onChange={(event) => handleInvestorsChange(event.target.value)}
          placeholder={"One per line. Use `Investor Name | https://website.com` to add URLs."}
        />
      </label>

      <div className="mt-5 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted-foreground">Source documents</span>
          <button
            type="button"
            onClick={handleAddSource}
            className="text-xs font-medium text-primary hover:underline"
          >
            Add source
          </button>
        </div>

        {(event.source_documents ?? []).length === 0 && (
          <p className="rounded-md border border-dashed bg-muted/40 p-3 text-xs text-muted-foreground">
            No sources attached. Add links to ensure this announcement is traceable.
          </p>
        )}

        {(event.source_documents ?? []).map((source, index) => (
          <div key={`${source.url || source.title || "source"}-${index}`} className="rounded-md border bg-card/60 p-3">
            <div className="flex items-start justify-between">
              <h4 className="text-xs font-semibold text-muted-foreground">Source #{index + 1}</h4>
              <button
                type="button"
                onClick={() => handleRemoveSource(index)}
                className="text-[11px] font-medium text-destructive hover:underline"
              >
                Remove
              </button>
            </div>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <label className="space-y-1 text-[11px] font-medium text-muted-foreground">
                Title
                <input
                  type="text"
                  className="w-full rounded-md border bg-background px-3 py-2 text-xs"
                  value={source.title ?? ""}
                  onChange={(event) => handleSourceField(index, "title", event.target.value)}
                />
              </label>
              <label className="space-y-1 text-[11px] font-medium text-muted-foreground">
                Publisher
                <input
                  type="text"
                  className="w-full rounded-md border bg-background px-3 py-2 text-xs"
                  value={source.publisher ?? ""}
                  onChange={(event) => handleSourceField(index, "publisher", event.target.value)}
                />
              </label>
              <label className="space-y-1 text-[11px] font-medium text-muted-foreground md:col-span-2">
                URL
                <input
                  type="url"
                  className="w-full rounded-md border bg-background px-3 py-2 text-xs"
                  value={source.url ?? ""}
                  onChange={(event) => handleSourceField(index, "url", event.target.value)}
                  placeholder="https://"
                />
              </label>
              <label className="space-y-1 text-[11px] font-medium text-muted-foreground">
                Published at
                <input
                  type="text"
                  className="w-full rounded-md border bg-background px-3 py-2 text-xs"
                  value={source.published_at ?? ""}
                  onChange={(event) => handleSourceField(index, "published_at", event.target.value)}
                  placeholder="2025-08-07T00:00:00Z"
                />
              </label>
              <label className="space-y-1 text-[11px] font-medium text-muted-foreground">
                Snippet
                <textarea
                  className="w-full rounded-md border bg-background px-3 py-2 text-xs"
                  rows={2}
                  value={source.snippet ?? ""}
                  onChange={(event) => handleSourceField(index, "snippet", event.target.value)}
                  placeholder="Optional excerpt"
                />
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
