import { NextRequest, NextResponse } from "next/server";

/**
 * POST /api/auth/session - Store JWT as httpOnly secure cookie
 * Called after Better Auth login/signup to persist the JWT for backend API calls.
 */
export async function POST(request: NextRequest) {
  try {
    const { token } = await request.json();

    if (!token || typeof token !== "string") {
      return NextResponse.json({ error: "Token is required" }, { status: 400 });
    }

    const response = NextResponse.json({ success: true });

    response.cookies.set("session_token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 60 * 60 * 24 * 7, // 7 days (matches Better Auth session)
    });

    // Also set a lightweight flag cookie the middleware can read
    // (middleware can't read httpOnly cookies in Next.js edge runtime)
    response.cookies.set("has_session", "1", {
      httpOnly: false,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });

    return response;
  } catch {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}

/**
 * GET /api/auth/session - Retrieve the JWT from httpOnly cookie
 * Called by the API client before making requests to FastAPI.
 */
export async function GET(request: NextRequest) {
  const token = request.cookies.get("session_token")?.value;

  if (!token) {
    return NextResponse.json({ token: null, authenticated: false }, { status: 401 });
  }

  // Basic expiry check: decode payload (no verification - that's FastAPI's job)
  try {
    const parts = token.split(".");
    if (parts.length === 3) {
      const payload = JSON.parse(
        Buffer.from(parts[1], "base64url").toString("utf-8")
      );
      if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
        // Token expired - clear cookies
        const response = NextResponse.json(
          { token: null, authenticated: false, reason: "expired" },
          { status: 401 }
        );
        response.cookies.delete("session_token");
        response.cookies.delete("has_session");
        return response;
      }
    }
  } catch {
    // If decode fails, let FastAPI handle verification
  }

  return NextResponse.json({ token, authenticated: true });
}

/**
 * DELETE /api/auth/session - Clear the session cookies (logout)
 */
export async function DELETE() {
  const response = NextResponse.json({ success: true });
  response.cookies.delete("session_token");
  response.cookies.delete("has_session");
  return response;
}
