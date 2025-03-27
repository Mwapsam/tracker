import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

function getUserRole(accessToken: string): string | null {
  try {
    const [, payload] = accessToken.split(".");
    const decoded = JSON.parse(atob(payload));
    return decoded.role;
  } catch {
    return null;
  }
}

const publicRoutes = ["/login", "/password"];
const adminRoutes = [
  "/admin",
  "/admin/logs",
  "/admin/trips",
  "/admin/trips/create",
  "/admin/trips/[id]/edit",
];
const driverRoutes = ["/driver", "/driver/dashboard", "/driver/trips"];

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const accessToken = request.cookies.get("accessToken")?.value;
  const userRole = accessToken ? getUserRole(accessToken) : null;

  const isPublicRoute = publicRoutes.includes(path);
  const isAdminRoute = adminRoutes.some((route) => path.startsWith(route));
  const isDriverRoute = driverRoutes.some((route) => path.startsWith(route));

  if (!accessToken && !isPublicRoute && (isAdminRoute || isDriverRoute)) {
    return NextResponse.redirect(new URL("/login", request.nextUrl));
  }

  if (isPublicRoute && accessToken) {
    if (userRole === "admin") {
      return NextResponse.redirect(new URL("/admin", request.nextUrl));
    }
    if (userRole === "driver") {
      return NextResponse.redirect(new URL("/driver", request.nextUrl));
    }
  }

  if (isAdminRoute && userRole !== "admin") {
    return NextResponse.redirect(new URL("/driver/dashboard", request.nextUrl));
  }

  if (isDriverRoute && userRole !== "driver") {
    return NextResponse.redirect(new URL("/admin", request.nextUrl));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|auth|_next/static|_next/image|favicon.ico).*)"],
};
