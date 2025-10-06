import { NextResponse } from "next/server";

import { getLatestDigestRecord, isDigestRoot, saveDigest, type DigestRoot } from "@/lib/getDigest";

export async function GET() {
  try {
    const record = await getLatestDigestRecord();
    if (record) {
      return NextResponse.json(record);
    }
    return NextResponse.json({
      run_id: null,
      created_at: null,
      data: {
        company_funding_digests: [],
        summary: "No data to display yet.",
      } as DigestRoot,
    });
  } catch (error) {
    console.error("[api/digest] Failed to read digest", error);
    return NextResponse.json({ error: "Failed to read digest" }, { status: 500 });
  }
}

async function handleWrite(request: Request) {
  try {
    const body = (await request.json()) as unknown;

    let digest: DigestRoot | null = null;
    let runId: string | undefined;

    if (isDigestRoot(body)) {
      digest = body;
    } else if (body && typeof body === "object" && "data" in body) {
      const candidate = (body as { data?: unknown; run_id?: unknown }).data;
      const providedRun = (body as { run_id?: unknown }).run_id;
      if (isDigestRoot(candidate)) {
        digest = candidate;
      }
      if (typeof providedRun === "string" && providedRun.length > 0) {
        runId = providedRun;
      }
    }

    if (!digest) {
      return NextResponse.json({ error: "Invalid digest payload" }, { status: 400 });
    }

    const record = await saveDigest(digest, { runId });
    return NextResponse.json(record);
  } catch (error) {
    console.error("[api/digest] Failed to write digest", error);
    return NextResponse.json({ error: "Failed to write digest" }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  return handleWrite(request);
}

export async function POST(request: Request) {
  return handleWrite(request);
}
