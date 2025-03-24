import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const adminRoutes = ["/admin", "/admin/dashboard", "/admin/settings"];
const driverRoutes = ["/driver", "/driver/profile", "/driver/trips"];
const protectedRoutes = [
  "/",
  "/logs",
  "/logs/[id]",
  "/trips/create",
  "/trips/[id]",
  "/trips",
  "/trips/[id]/edit",
];
const publicRoutes = ["/login", "/password"];

function getUserRole(accessToken: string) {
  try {
    const [, payload] = accessToken.split(".");
    const decoded = JSON.parse(atob(payload));
    console.log("DECODED: ", decoded);
    
    return decoded.is_staff ? "admin" : "driver";
  } catch {
    return null;
  }
}

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const accessToken = request.cookies.get("accessToken")?.value;
  const userRole = accessToken ? getUserRole(accessToken) : null;

  if (publicRoutes.includes(path)) {
    if (accessToken) {
      return NextResponse.redirect(new URL("/", request.nextUrl));
    }
    return NextResponse.next();
  }

  if (
    protectedRoutes.includes(path) ||
    adminRoutes.includes(path) ||
    driverRoutes.includes(path)
  ) {
    if (!accessToken || accessToken.trim() === "") {
      const response = NextResponse.redirect(
        new URL("/login", request.nextUrl)
      );
      response.cookies.set("accessToken", "", { path: "/", maxAge: 0 });
      return response;
    }
    if (adminRoutes.includes(path) && userRole !== "admin") {
      return NextResponse.redirect(new URL("/", request.nextUrl));
    }
    if (driverRoutes.includes(path) && userRole !== "driver") {
      return NextResponse.redirect(new URL("/", request.nextUrl));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|auth|_next/static|_next/image|favicon.ico).*)"],
};
