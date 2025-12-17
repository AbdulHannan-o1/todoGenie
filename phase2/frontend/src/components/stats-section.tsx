// This component is no longer used in the new design
// Kept for reference or future use if needed

export default function StatsSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 border-t">
      <div className="container px-4 md:px-6 text-center">
        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
          Join thousands of productive users
        </h2>
        <div className="grid gap-8 md:grid-cols-3 mt-8">
          <div className="flex flex-col items-center space-y-2">
            <div className="text-5xl font-bold text-primary">10K+</div>
            <p className="text-muted-foreground">Tasks Completed Daily</p>
          </div>
          <div className="flex flex-col items-center space-y-2">
            <div className="text-5xl font-bold text-primary">99%</div>
            <p className="text-muted-foreground">User Satisfaction</p>
          </div>
          <div className="flex flex-col items-center space-y-2">
            <div className="text-5xl font-bold text-primary">24/7</div>
            <p className="text-muted-foreground">Reliable Service</p>
          </div>
        </div>
      </div>
    </section>
  );
}
