import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('x-tenant-domain') || request.headers.get('host') || ''
  const domain = hostname.split(':')[0]

  const response = NextResponse.next()
  response.headers.set('x-tenant-domain', domain)

  const token = request.cookies.get('access_token')?.value
  const pathname = request.nextUrl.pathname
  const isAuthPage = pathname.startsWith('/login') || pathname.startsWith('/pin')
  const isPublicAsset = /\.(ico|png|svg|jpg|jpeg|webp|css|js|woff|woff2)$/.test(pathname)

  if (isPublicAsset) {
    return response
  }

  if (!token && !isAuthPage) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/pos', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|icons|manifest|sw\\.js).*)'],
}
