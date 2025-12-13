"use client";

import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function HomePage() {
  const { isAuthenticated, user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  const handleLogout = () => {
    logout();
    toast.info("You have been logged out.");
    router.push("/login");
  };

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
        Loading or redirecting...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background text-foreground p-4">
      <h1 className="text-4xl font-bold mb-4">Welcome, {user?.email}!</h1>
      <p className="text-lg mb-8">This is your authenticated home page.</p>
      <Button onClick={handleLogout}>Logout</Button>
    </div>
  );
}
