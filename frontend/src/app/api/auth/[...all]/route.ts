// Better Auth API route handler for Next.js App Router
import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest, NextResponse } from "next/server";

const { GET: _GET, POST: _POST } = toNextJsHandler(auth);

/**
 * Fix the request URL: strip trailing slash that Next.js adds
 * because of trailingSlash: true in next.config.js.
 * Better Auth's router doesn't recognize paths with trailing slashes.
 *
 * We create a standard Request (not NextRequest) to avoid any
 * framework-specific URL handling issues.
 */
function fixUrl(req: Request): string {
  const url = new URL(req.url);
  if (url.pathname.endsWith("/") && url.pathname.length > 1) {
    url.pathname = url.pathname.slice(0, -1);
  }
  return url.toString();
}

export async function GET(req: NextRequest) {
  try {
    const fixedUrl = fixUrl(req);
    // Use standard Request to avoid NextRequest URL quirks
    const fixedReq = new Request(fixedUrl, {
      method: "GET",
      headers: req.headers,
    });
    const response = await auth.handler(fixedReq);
    return response;
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
    const fixedUrl = fixUrl(req);
    const bodyText = await req.text();
    // Use standard Request to avoid NextRequest URL quirks
    const fixedReq = new Request(fixedUrl, {
      method: "POST",
      headers: req.headers,
      body: bodyText,
    });
    const response = await auth.handler(fixedReq);
    return response;
  } catch (error: any) {
    console.error("[Better Auth POST]", error);
    return NextResponse.json(
      { error: "Auth service error", detail: String(error?.message || error) },
      { status: 500 }
    );
  }
}
