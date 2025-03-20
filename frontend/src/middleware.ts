import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/"];
const publicRoutes = ["/login", "/password"];

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const isProtectedRoute = protectedRoutes.includes(path);
  const isPublicRoute = publicRoutes.includes(path);

  const accessToken = request.cookies.get("accessToken")?.value;

  if (isProtectedRoute && (!accessToken || accessToken.trim() === "")) {
    const response = NextResponse.redirect(new URL("/login", request.nextUrl));
    response.cookies.set("accessToken", "", { path: "/", maxAge: 0 });
    return response;
  }

  if (isPublicRoute && accessToken) {
    return NextResponse.redirect(new URL("/", request.nextUrl));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|auth|_next/static|_next/image|favicon.ico).*)"],
};
