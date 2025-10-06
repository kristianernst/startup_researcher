import { getDigest } from "@/lib/getDigest";
import { DigestReport } from "@/components/DigestReport";

export const dynamic = "force-dynamic";

export default async function Home() {
  const data = await getDigest();
  return <DigestReport data={data} />;
}
