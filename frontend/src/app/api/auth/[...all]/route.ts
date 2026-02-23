// Better Auth API route handler for Next.js App Router
import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";

const handler = toNextJsHandler(auth);

/**
 * Strip trailing slash from the request URL before passing to Better Auth.
 * next.config.js has trailingSlash: true, which appends "/" to all paths.
 * Better Auth's internal router does NOT match paths with trailing slashes
 * (e.g. /api/auth/sign-up/email/ → 404, but /api/auth/sign-up/email → 200).
 */
async function stripTrailingSlash(req: Request): Promise<Request> {
  const url = new URL(req.url);
  if (url.pathname.length > 1 && url.pathname.endsWith("/")) {
    url.pathname = url.pathname.slice(0, -1);
    // Clone the request properly to preserve headers and body
    const body = req.method !== "GET" && req.method !== "HEAD"
      ? await req.arrayBuffer()
      : undefined;
    return new Request(url.toString(), {
      method: req.method,
      headers: req.headers,
      body: body,
    });
  }
  return req;
}

export async function GET(req: Request) {
  try {
    const fixedReq = await stripTrailingSlash(req);
    return await handler.GET(fixedReq);
  } catch (error: any) {
    console.error("[Better Auth GET] Error:", error?.message || error);
    return new Response(
      JSON.stringify({ error: "Auth service error", detail: error?.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function POST(req: Request) {
  try {
    const fixedReq = await stripTrailingSlash(req);
    return await handler.POST(fixedReq);
  } catch (error: any) {
    console.error("[Better Auth POST] Error:", error?.message || error);
    return new Response(
      JSON.stringify({ error: "Auth service error", detail: error?.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
