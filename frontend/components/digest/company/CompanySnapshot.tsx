import type { CompanyDigest } from "@/lib/getDigest";

interface CompanySnapshotProps {
  company: CompanyDigest["company"];
}

export function CompanySnapshot({ company }: CompanySnapshotProps) {
  const owners = company.owners?.filter(Boolean) ?? [];
  const domain = company.website
    ? (() => {
        try {
          return new URL(company.website).hostname.replace(/^www\./, "");
        } catch {
          return company.website;
        }
      })()
    : null;

  const rows: Array<{ label: string; value: string; isLink?: boolean }> = [
    { label: "Founders", value: owners.length ? owners.join(" · ") : "—" },
    { label: "Industry", value: company.industry || "—" },
    { label: "Location", value: company.location?.country || "—" },
    { label: "Employees", value: company.num_employees ? String(company.num_employees) : "—" },
    {
      label: "Website",
      value: company.website ? domain || company.website : "—",
      isLink: Boolean(company.website),
    },
  ];

  return (
    <section>
      <h4 className="mb-5 text-sm font-semibold tracking-tight">Company details</h4>
      <dl className="grid grid-cols-1 gap-x-8 gap-y-5 text-sm text-foreground/75 sm:grid-cols-2 lg:grid-cols-3">
        {rows.map((row) => (
          <div key={row.label}>
            <dt className="mb-1 text-xs uppercase tracking-[0.14em] text-foreground/60 font-normal">{row.label}</dt>
            <dd className="text-foreground">
              {row.isLink && company.website ? (
                <a
                  href={company.website}
                  target="_blank"
                  rel="noreferrer"
                  className="underline decoration-transparent underline-offset-4 transition hover:decoration-foreground/60"
                >
                  {row.value}
                </a>
              ) : (
                row.value
              )}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
