// Better Auth API route handler for Next.js App Router
import { NextRequest, NextResponse } from "next/server";

/**
 * Lazily import auth to catch initialization errors.
 */
async function getHandler() {
  try {
    const { auth } = await import("@/lib/auth-server");
    const { toNextJsHandler } = await import("better-auth/next-js");
    return toNextJsHandler(auth);
  } catch (error: any) {
    console.error("[Better Auth] Failed to initialize:", error);
    throw error;
  }
}

/**
 * Strip trailing slash from the request URL before passing to Better Auth.
 * next.config.js has trailingSlash: true, which appends "/" to all paths.
 * Better Auth's internal router does NOT match paths with trailing slashes.
 */
async function fixRequest(req: NextRequest): Promise<Request> {
  const url = new URL(req.url);
  if (url.pathname.length > 1 && url.pathname.endsWith("/")) {
    url.pathname = url.pathname.slice(0, -1);
  }

  // Always create a clean Request for Better Auth
  const headers = new Headers(req.headers);
  const body = req.method !== "GET" && req.method !== "HEAD"
    ? await req.text()
    : undefined;

  return new Request(url.toString(), {
    method: req.method,
    headers,
    body,
  });
}

function errorResponse(error: any, context: string) {
  const message = error?.message || String(error) || "Unknown error";
  console.error(`[Better Auth ${context}]`, message);
  return NextResponse.json(
    { error: "Auth service error", detail: message },
    { status: 500 }
  );
}

export async function GET(req: NextRequest) {
  try {
    const handler = await getHandler();
    const fixedReq = await fixRequest(req);
    const response = await handler.GET(fixedReq);
    return response;
  } catch (error: any) {
    return errorResponse(error, "GET");
  }
}

export async function POST(req: NextRequest) {
  try {
    const handler = await getHandler();
    const fixedReq = await fixRequest(req);
    const response = await handler.POST(fixedReq);
    return response;
  } catch (error: any) {
    return errorResponse(error, "POST");
  }
}
