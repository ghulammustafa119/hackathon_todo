// Debug endpoint - check Better Auth env vars and test handler
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const result: any = {
    database_url_set: !!process.env.DATABASE_URL,
    better_auth_secret_set: !!process.env.BETTER_AUTH_SECRET,
    better_auth_url: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "not set",
    node_env: process.env.NODE_ENV,
  };

  // Test auth.handler with /ok path
  try {
    const { auth } = await import("@/lib/auth-server");
    const baseURL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000";
    const testReq = new Request(`${baseURL}/api/auth/ok`, { method: "GET" });
    const response = await auth.handler(testReq);
    result.handler_ok_status = response.status;
    result.handler_ok_body = await response.text();
  } catch (error: any) {
    result.handler_error = String(error?.message || error);
  }

  return NextResponse.json(result);
}

export async function POST(req: NextRequest) {
  // Test signup via auth.api directly
  try {
    const body = await req.json();
    const { auth } = await import("@/lib/auth-server");

    // Try calling auth.api.signUpEmail directly
    const signupResult = await auth.api.signUpEmail({
      body: {
        email: body.email,
        password: body.password,
        name: body.name,
      },
    });

    return NextResponse.json({ success: true, data: signupResult });
  } catch (error: any) {
    // Also check the database schema
    let schema: any = null;
    try {
      const { Pool } = await import("pg");
      const pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: { rejectUnauthorized: false },
      });
      const res = await pool.query(`
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'user'
        ORDER BY ordinal_position
      `);
      schema = res.rows;
      await pool.end();
    } catch {}

    return NextResponse.json(
      {
        success: false,
        error: String(error?.message || error),
        cause: error?.cause ? String(error.cause) : undefined,
        stack: error?.stack?.split("\n").slice(0, 8),
        user_table_schema: schema,
      },
      { status: 500 }
    );
  }
}
