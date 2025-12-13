import Hero from "../components/hero";
import FeatureHighlights from "../components/feature-highlights";
import StatsSection from "../components/stats-section";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <Hero />
      <FeatureHighlights />
      <StatsSection />
    </div>
  );
}