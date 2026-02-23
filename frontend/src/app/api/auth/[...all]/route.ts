// Better Auth API route handler for Next.js App Router
import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest, NextResponse } from "next/server";

const { GET: _GET, POST: _POST } = toNextJsHandler(auth);

export async function GET(req: NextRequest) {
  try {
    // Strip trailing slash by modifying the URL via nextUrl
    if (req.nextUrl.pathname.endsWith("/") && req.nextUrl.pathname.length > 1) {
      const url = req.nextUrl.clone();
      url.pathname = url.pathname.slice(0, -1);
      const newReq = new NextRequest(url, { headers: req.headers });
      return await _GET(newReq);
    }
    return await _GET(req);
  } catch (error: any) {
    console.error("[Better Auth GET]", error);
    return NextResponse.json(
      { error: "Auth service error", detail: String(error?.message || error) },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    // For POST, we need to clone with body preserved
    if (req.nextUrl.pathname.endsWith("/") && req.nextUrl.pathname.length > 1) {
      const url = req.nextUrl.clone();
      url.pathname = url.pathname.slice(0, -1);
      // Read body before creating new request
      const bodyText = await req.text();
      const newReq = new NextRequest(url, {
        method: "POST",
        headers: req.headers,
        body: bodyText,
      });
      return await _POST(newReq);
    }
    return await _POST(req);
  } catch (error: any) {
    console.error("[Better Auth POST]", error);
    return NextResponse.json(
      { error: "Auth service error", detail: String(error?.message || error) },
      { status: 500 }
    );
  }
}
