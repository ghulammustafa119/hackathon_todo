// Auth API catch-all route - returns 404 as auth is handled by backend API directly
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ error: "Auth is handled by backend API" }, { status: 404 });
}

export async function POST() {
  return NextResponse.json({ error: "Auth is handled by backend API" }, { status: 404 });
}
