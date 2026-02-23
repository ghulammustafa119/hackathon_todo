// Run Better Auth database migrations
// GET /api/auth/migrate - check what migrations are needed
// POST /api/auth/migrate - run migrations to create tables
import { NextResponse } from "next/server";
import { getMigrations } from "better-auth/db";
import { authOptions } from "@/lib/auth-server";

export async function POST() {
  try {
    const { toBeCreated, toBeAdded, runMigrations } = await getMigrations(authOptions as any);

    if (toBeCreated.length === 0 && toBeAdded.length === 0) {
      return NextResponse.json({
        message: "No migrations needed",
        toBeCreated: [],
        toBeAdded: [],
      });
    }

    await runMigrations();

    return NextResponse.json({
      message: "Migrations completed successfully",
      toBeCreated,
      toBeAdded,
    });
  } catch (error: any) {
    console.error("[Better Auth Migration] Error:", error);
    return NextResponse.json(
      { error: "Migration failed", detail: String(error?.message || error) },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const { toBeCreated, toBeAdded } = await getMigrations(authOptions as any);

    return NextResponse.json({
      needsMigration: toBeCreated.length > 0 || toBeAdded.length > 0,
      toBeCreated,
      toBeAdded,
    });
  } catch (error: any) {
    console.error("[Better Auth Migration Check] Error:", error);
    return NextResponse.json(
      { error: "Migration check failed", detail: String(error?.message || error) },
      { status: 500 }
    );
  }
}
