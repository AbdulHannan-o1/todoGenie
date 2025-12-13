"use client";

import Link from "next/link";
import { ModeToggle } from "../theme-toggle";
import { Button } from "../ui/button";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    toast.info("You have been logged out.");
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="text-2xl font-bold">
          TodoGenie
        </Link>
        <nav className="flex items-center space-x-4">
          {isAuthenticated ? (
            <>
              <Link href="/home" className="text-sm font-medium hover:underline">
                Home
              </Link>
              <Button variant="ghost" onClick={handleLogout}>
                Logout
              </Button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-sm font-medium hover:underline">
                Login
              </Link>
              <Link href="/signup" className="text-sm font-medium hover:underline">
                Sign Up
              </Link>
            </>
          )}
          <ModeToggle />
        </nav>
      </div>
    </header>
  );
}
