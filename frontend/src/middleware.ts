import { NextRequest, NextResponse } from 'next/server';

const PROTECTED_PATHS = ['/dashboard'];

export function middleware(request: NextRequest) {
  const currentPath = request.nextUrl.pathname;

  const isProtectedPath = PROTECTED_PATHS.some(
    path => currentPath === path || currentPath.startsWith(path + '/')
  );

  if (!isProtectedPath) {
    return addSecurityHeaders(NextResponse.next());
  }

  // Check for auth indicators:
  // 1. Better Auth session cookie (set by Better Auth automatically)
  // 2. Our httpOnly session_token (set by /api/auth/session POST)
  // 3. Lightweight has_session flag (set alongside httpOnly cookie)
  const betterAuthSession = request.cookies.get('better-auth.session_token')?.value;
  const sessionToken = request.cookies.get('session_token')?.value;
  const hasSession = request.cookies.get('has_session')?.value;

  const hasAuth = !!betterAuthSession || !!sessionToken || !!hasSession;

  if (!hasAuth) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = '/login';
    loginUrl.searchParams.set('redirect', currentPath);
    return NextResponse.redirect(loginUrl);
  }

  // If we have session_token, do a lightweight expiry check
  // (Real verification happens server-side in FastAPI)
  if (sessionToken) {
    try {
      const parts = sessionToken.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(
          Buffer.from(parts[1], 'base64url').toString('utf-8')
        );
        if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
          // Token expired - clear and redirect
          const loginUrl = request.nextUrl.clone();
          loginUrl.pathname = '/login';
          const response = NextResponse.redirect(loginUrl);
          response.cookies.delete('session_token');
          response.cookies.delete('has_session');
          return response;
        }
      }
    } catch {
      // If decode fails, allow through - FastAPI will reject if truly invalid
    }
  }

  return addSecurityHeaders(NextResponse.next());
}

/**
 * Add standard security headers to all responses.
 */
function addSecurityHeaders(response: NextResponse): NextResponse {
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  return response;
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
    '/dashboard/:path*',
  ],
};
