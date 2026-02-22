import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Define protected routes
  const protectedPaths = ['/dashboard'];
  const currentPath = request.nextUrl.pathname;

  // Check if the current path is protected
  const isProtectedPath = protectedPaths.some(path =>
    currentPath === path || currentPath.startsWith(path + '/')
  );

  // Check for auth: Better Auth session cookie OR our JWT cookie
  const betterAuthSession = request.cookies.get('better-auth.session_token')?.value;
  const authToken = request.cookies.get('auth_token')?.value;
  const hasAuth = !!betterAuthSession || !!authToken;

  // If it's a protected route and user is not authenticated
  if (isProtectedPath && !hasAuth) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

// Define which paths the middleware should run on
export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
    '/dashboard/:path*',
  ],
};
