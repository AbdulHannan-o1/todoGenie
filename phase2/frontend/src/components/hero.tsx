import Link from "next/link";

export default function Hero() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 border-b">
      <div className="container px-4 md:px-6 text-center">
        <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
          Welcome to TodoGenie
        </h1>
        <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400 mt-4">
          Your intelligent task management companion. Organize, prioritize, and conquer your day.
        </p>
        <div className="space-x-4 mt-6">
          <Link
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
            href="/signup"
          >
            Sign Up
          </Link>
          <Link
            className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-8 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
            href="/login"
          >
            Login
          </Link>
        </div>
      </div>
    </section>
  );
}
