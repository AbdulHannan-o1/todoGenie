import Hero from "../components/hero";
import FeatureSlider from "../components/feature-slider";
import FeaturesSection from "../components/features-section";
import CTASection from "../components/cta-section";
import Footer from "../components/footer";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Hero />
      <FeatureSlider />
      <FeaturesSection />
      <CTASection />
      <Footer />
    </div>
  );
}