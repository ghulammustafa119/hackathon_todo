// Debug endpoint - check if Better Auth env vars are configured
// Safe to keep in production (only shows boolean flags, no secrets)
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    database_url_set: !!process.env.DATABASE_URL,
    better_auth_secret_set: !!process.env.BETTER_AUTH_SECRET,
    better_auth_url: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "not set",
    node_env: process.env.NODE_ENV,
  });
}
