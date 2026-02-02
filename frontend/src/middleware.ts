import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Define protected routes
  const protectedPaths = ['/dashboard'];
  const currentPath = request.nextUrl.pathname;

  // Check if the current path is protected
  const isProtectedPath = protectedPaths.some(path =>
    currentPath === path || currentPath.startsWith(path + '/')
  );

  // Get the auth token from cookies
  const token = request.cookies.get('auth_token')?.value || null;

  // If it's a protected route and user is not authenticated
  if (isProtectedPath && !token) {
    // Redirect to login page
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  // Allow the request to proceed
  return NextResponse.next();
}

// Define which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
    // Specifically protect dashboard routes
    '/dashboard/:path*',
  ],
};