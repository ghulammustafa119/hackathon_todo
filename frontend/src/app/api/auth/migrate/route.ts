// Run Better Auth database migrations
// GET /api/auth/migrate - check what migrations are needed
// POST /api/auth/migrate - run migrations to create tables
import { NextResponse } from "next/server";
import { getMigrations } from "better-auth/db";
import { authOptions } from "@/lib/auth-server";
import { Pool } from "pg";

/**
 * Fix existing data before running migrations.
 * Better Auth requires certain columns (emailVerified, createdAt, updatedAt)
 * that may not exist or may have nulls in pre-existing user rows.
 */
async function preMigrationFixes() {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });

  try {
    // Add missing columns with defaults if they don't exist
    const fixes = [
      `ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "emailVerified" BOOLEAN DEFAULT false`,
      `ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "image" TEXT`,
      `ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "createdAt" TIMESTAMP DEFAULT NOW()`,
      `ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "updatedAt" TIMESTAMP DEFAULT NOW()`,
      // Update any null values
      `UPDATE "user" SET "emailVerified" = false WHERE "emailVerified" IS NULL`,
      `UPDATE "user" SET "createdAt" = NOW() WHERE "createdAt" IS NULL`,
      `UPDATE "user" SET "updatedAt" = NOW() WHERE "updatedAt" IS NULL`,
    ];

    for (const sql of fixes) {
      try {
        await pool.query(sql);
      } catch (err: any) {
        // Column might already exist or have a different type - that's OK
        console.log(`[Migration] SQL note: ${err.message}`);
      }
    }
  } finally {
    await pool.end();
  }
}

export async function POST() {
  try {
    // Fix existing data first
    await preMigrationFixes();

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
      tablesCreated: toBeCreated.map((t: any) => t.table),
      fieldsAdded: toBeAdded.map((t: any) => ({ table: t.table, fields: Object.keys(t.fields) })),
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
      toBeCreated: toBeCreated.map((t: any) => t.table),
      toBeAdded: toBeAdded.map((t: any) => ({ table: t.table, fields: Object.keys(t.fields) })),
    });
  } catch (error: any) {
    console.error("[Better Auth Migration Check] Error:", error);
    return NextResponse.json(
      { error: "Migration check failed", detail: String(error?.message || error) },
      { status: 500 }
    );
  }
}
