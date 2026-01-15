"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import apiClient from "@/lib/api-client";
import { userApi } from "@/lib/api/user";
import { toast } from "sonner";
import { Eye, EyeOff } from 'lucide-react';

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { login: authLogin } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Basic validation
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      toast.error("Password must be at least 6 characters long");
      return;
    }

    setLoading(true);
    try {
      // Register the user
      await apiClient.post("/auth/register", {
        email,
        username, // Send username instead of name
        password
      });

      // Now log the user in automatically
      const formData = new URLSearchParams();
      formData.append('username', email);  // OAuth2 expects 'username' field (can be email)
      formData.append('password', password);

      const response = await apiClient.post("/auth/token", formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        }
      });
      const { access_token } = response.data;

      // Set the token in the API client so we can make authenticated requests
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Fetch the current user's information
      const userData = await userApi.getCurrentUser();

      // Login with the actual user data including the ID
      authLogin(access_token, userData);
      toast.success("Registration and login successful!");
      router.push("/home"); // Redirect to home page after successful registration and login
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail || "Registration failed. Please try again.";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 p-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800/80 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
            <p className="text-slate-400">Join TodoGenie today</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="fullName" className="text-slate-300">Full Name</Label>
              <Input
                id="fullName"
                type="text"
                placeholder="John Doe"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500"
              />
            </div>

            <div>
              <Label htmlFor="username" className="text-slate-300">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="johndoe"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500"
              />
            </div>

            <div>
              <Label htmlFor="email" className="text-slate-300">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-slate-300">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500 pr-10"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-white"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div>
              <Label htmlFor="confirmPassword" className="text-slate-300">Confirm Password</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500 pr-10"
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-white"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-cyan-600 text-white rounded-md font-medium shadow transition-colors hover:bg-cyan-700 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-slate-400 text-sm">
              Already have an account?{" "}
              <Link href="/login" className="text-cyan-400 hover:text-cyan-300 font-medium">
                Log In
              </Link>
            </p>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-slate-500 text-xs">
            By signing up, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
}
