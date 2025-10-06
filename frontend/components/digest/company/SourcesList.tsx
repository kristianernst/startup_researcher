import type { SourceDocument } from "@/lib/getDigest";

interface SourcesListProps {
  sources: SourceDocument[];
}

export function SourcesList({ sources }: SourcesListProps) {
  if (sources.length === 0) return null;

  return (
    <div className="space-y-2 text-left text-sm text-foreground/75">
      <span className="text-xs uppercase tracking-[0.16em] text-foreground/60 font-normal">Sources</span>
      <ul className="flex flex-wrap gap-2">
        {sources.map((source, index) => {
          const label = source.publisher || source.title || "Source";
          const key = `${source.url || label}-${index}`;
          return (
            <li key={key} className="flex items-center gap-2">
              {source.url ? (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="underline decoration-foreground/40 underline-offset-4 text-foreground/80 transition hover:decoration-foreground hover:text-foreground"
                >
                  {label}
                </a>
              ) : (
                <span className="text-foreground/70">{label}</span>
              )}
              {index < sources.length - 1 && <span aria-hidden className="text-foreground/30">/</span>}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
