import type { CompanyDigest, SourceDocument } from "@/lib/getDigest";
import { SourcesList } from "./SourcesList";

interface CompanyHeaderProps {
  company: CompanyDigest["company"];
  sources: SourceDocument[];
}

export function CompanyHeader({ company, sources }: CompanyHeaderProps) {
  const safeSources = sources.filter((source): source is SourceDocument => Boolean(source));

  return (
    <section className="flex flex-col">
      <h3 className="text-2xl font-semibold tracking-tight leading-none sm:text-3xl">
        {company.website ? (
          <a
            href={company.website}
            target="_blank"
            rel="noreferrer"
            className="underline decoration-transparent transition hover:decoration-foreground/60"
          >
            {company.name}
          </a>
        ) : (
          company.name
        )}
      </h3>
      {company.brief && <p className="mt-4 text-sm leading-relaxed text-foreground/75 sm:text-base">{company.brief}</p>}
      
      <div className="mt-6">
        <SourcesList sources={safeSources} />
      </div>
    </section>
  );
}
