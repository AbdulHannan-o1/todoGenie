'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export default function CTASection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-r from-slate-800 to-slate-900">
      <div className="container px-4 md:px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-white mb-4">
            Ready to Transform Your Productivity?
          </h2>
          <p className="text-slate-300 max-w-[600px] mx-auto md:text-xl mb-8">
            Join thousands of users who have revolutionized their task management
          </p>
          <Link
            href="/signup"
            className="inline-flex h-12 items-center justify-center rounded-md bg-cyan-600 px-8 text-sm font-medium text-white shadow transition-colors hover:bg-cyan-700 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            Start Using Now
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </motion.div>
      </div>
    </section>
  );
}