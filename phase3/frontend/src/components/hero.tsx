'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Check, Sparkles } from 'lucide-react';

export default function Hero() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-b from-slate-900 to-slate-800 flex items-center justify-center">
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_1fr] lg:gap-12 items-center">
          <motion.div
            className="flex flex-col justify-center space-y-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="space-y-2">
              <div className="inline-flex items-center rounded-lg bg-slate-800 text-sm text-slate-300 px-3 py-1">
                <Sparkles className="h-4 w-4 mr-2" />
                AI-Powered Task Management
              </div>
              <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl md:text-6xl text-white">
                Master Your Tasks with AI-Powered Intelligence
              </h1>
              <p className="max-w-[700px] text-slate-300 md:text-xl">
                Manage tasks effortlessly with natural language. From simple todos to recurring reminders, our AI chatbot handles it all.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Link
                href="/signup"
                className="inline-flex h-12 items-center justify-center rounded-md bg-cyan-600 px-8 text-sm font-medium text-white shadow transition-colors hover:bg-cyan-700 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                Get Started for Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex h-12 items-center justify-center rounded-md border border-slate-700 bg-transparent px-8 text-sm font-medium text-slate-300 shadow-sm transition-colors hover:bg-slate-800 hover:text-white focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                Log In
              </Link>
            </div>
            <div className="pt-4">
              <div className="flex items-center space-x-2 text-sm text-slate-400">
                <Check className="h-4 w-4 text-cyan-500" />
                <span>No credit card required</span>
                <Check className="h-4 w-4 text-cyan-500 ml-4" />
                <span>Free forever plan</span>
              </div>
            </div>
          </motion.div>
          <motion.div
            className="flex items-center justify-center"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="relative w-full max-w-lg">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-2xl blur-xl"></div>
              <div className="relative bg-slate-800/80 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-300">Sample Tasks</span>
                    <span className="text-xs text-slate-500">Today</span>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                      <div className="h-4 w-4 rounded-full border border-slate-500"></div>
                      <span className="text-slate-200 text-sm">Complete project proposal</span>
                      <span className="ml-auto text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded">High</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                      <div className="h-4 w-4 rounded-full border border-cyan-500 bg-cyan-500/20"></div>
                      <span className="text-slate-200 text-sm line-through">Team meeting at 3 PM</span>
                      <span className="ml-auto text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Completed</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                      <div className="h-4 w-4 rounded-full border border-slate-500"></div>
                      <span className="text-slate-200 text-sm">Review documentation</span>
                      <span className="ml-auto text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">Medium</span>
                    </div>
                  </div>
                  <div className="pt-2 text-xs text-slate-500 text-center">
                    Clean task cards with statuses, tags, and priorities
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}