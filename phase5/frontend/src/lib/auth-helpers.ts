import { redirect } from "next/navigation";

export function redirectToHome() {
  redirect("/home");
}

export function redirectToLogin() {
  redirect("/login");
}
