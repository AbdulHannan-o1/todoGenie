'use client';

import { Bot, RefreshCcw, FolderKanban, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

export default function FeaturesSection() {
  const features = [
    {
      icon: Bot,
      title: "AI-Powered Chatbot",
      description: "Manage tasks with natural language. Just say 'Add grocery shopping tomorrow at 5 PM' and it's done."
    },
    {
      icon: RefreshCcw,
      title: "Smart Recurring Tasks",
      description: "Set it once, forget it. Weekly meetings, daily reminders—auto-rescheduled."
    },
    {
      icon: FolderKanban,
      title: "Advanced Organization",
      description: "Priorities, tags, search, filter, and sort. Find what you need instantly."
    },
    {
      icon: Lock,
      title: "Cloud-Native & Secure",
      description: "Your data is secure and accessible anywhere. Built on Kubernetes and serverless tech."
    }
  ];

  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-slate-950">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-white mb-4">
            Why Choose Our Todo App?
          </h2>
          <p className="text-slate-400 max-w-[600px] mx-auto md:text-xl">
            Powerful features designed to boost your productivity
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:bg-slate-800 transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <div className="p-3 bg-cyan-500/10 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                  <Icon className="h-6 w-6 text-cyan-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400">{feature.description}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}