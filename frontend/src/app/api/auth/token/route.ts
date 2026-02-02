import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { token } = await request.json();

    if (!token) {
      return NextResponse.json({ error: 'Token is required' }, { status: 400 });
    }

    // Create a response with a cookie containing the token
    const response = NextResponse.json({ success: true });

    // Set the auth token in a cookie
    response.cookies.set('auth_token', token, {
      httpOnly: false, // Make it accessible to middleware
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 24, // 24 hours
      path: '/',
      sameSite: 'strict',
    });

    return response;
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function DELETE() {
  const response = NextResponse.json({ success: true });

  // Clear the auth token cookie
  response.cookies.delete('auth_token');

  return response;
}