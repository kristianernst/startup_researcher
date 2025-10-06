import ReactMarkdown from "react-markdown";

interface DigestHeaderProps {
  monthLabel: string | null;
  summary?: string | null;
}

export function DigestHeader({ monthLabel, summary }: DigestHeaderProps) {
  return (
    <header className="mb-12 space-y-4 text-center">
      <div className="flex flex-col items-center gap-1 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground/80 sm:flex-row sm:justify-center sm:gap-3">
        <span>Monthly digest</span>
        {monthLabel && <span className="text-foreground/90">{monthLabel}</span>}
      </div>
      <h1 className="text-4xl font-semibold tracking-tight sm:text-[2.6rem]">Danish Startup Funding Review</h1>
      {summary && (
        <div className="mx-auto max-w-3xl text-base leading-relaxed text-foreground/75 sm:text-lg">
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      )}
    </header>
  );
}
