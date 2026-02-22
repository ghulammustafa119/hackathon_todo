// Better Auth server configuration
// This runs on the Next.js server side (API routes)
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Validate required environment variables at startup
if (!process.env.DATABASE_URL) {
  console.error(
    "FATAL: DATABASE_URL is not set. Better Auth cannot connect to the database. " +
    "Set DATABASE_URL in your environment variables (Vercel dashboard for production)."
  );
}

if (!process.env.BETTER_AUTH_SECRET) {
  console.error(
    "FATAL: BETTER_AUTH_SECRET is not set. Better Auth cannot sign sessions. " +
    "Set BETTER_AUTH_SECRET in your environment variables (Vercel dashboard for production)."
  );
}

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.DATABASE_URL ? { rejectUnauthorized: false } : undefined,
  }),
  emailAndPassword: {
    enabled: true,
  },
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
        // Use HS256 so FastAPI can verify with the same secret
        issuer: "better-auth",
      },
    }),
  ],
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});
