import { Bell, Layout, RefreshCcw } from "lucide-react";

export default function FeatureHighlights() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
      <div className="container px-4 md:px-6 text-center">
        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
          Features that empower you
        </h2>
        <p className="mx-auto max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed mt-4">
          Discover how TodoGenie helps you stay on top of your tasks.
        </p>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 mt-8">
          {/* Feature Card 1 */}
          <div className="flex flex-col items-center space-y-2">
            <div className="h-12 w-12 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
              <Bell className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold">Smart Reminders</h3>
            <p className="text-muted-foreground">
              Never miss a deadline with intelligent, customizable reminders.
            </p>
          </div>
          {/* Feature Card 2 */}
          <div className="flex flex-col items-center space-y-2">
            <div className="h-12 w-12 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
              <Layout className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold">Intuitive Interface</h3>
            <p className="text-muted-foreground">
              Manage your tasks with a clean, user-friendly design.
            </p>
          </div>
          {/* Feature Card 3 */}
          <div className="flex flex-col items-center space-y-2">
            <div className="h-12 w-12 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
              <RefreshCcw className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold">Cross-Device Sync</h3>
            <p className="text-muted-foreground">
              Access your tasks anytime, anywhere, on any device.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
