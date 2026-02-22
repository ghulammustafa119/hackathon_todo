// Better Auth API route handler for Next.js App Router
import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";

const handler = toNextJsHandler(auth);

// Wrap handlers with error catching so missing env vars don't cause silent 404
export async function GET(req: Request) {
  try {
    return await handler.GET(req);
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
    return await handler.POST(req);
  } catch (error: any) {
    console.error("[Better Auth POST] Error:", error?.message || error);
    return new Response(
      JSON.stringify({ error: "Auth service error", detail: error?.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
