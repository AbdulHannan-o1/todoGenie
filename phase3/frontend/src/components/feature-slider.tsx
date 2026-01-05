'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, ListChecks, Tag, Clock, Search, Repeat, Bell, MessageCircle, Users } from 'lucide-react';

const features = [
  {
    icon: ListChecks,
    title: "Add, Delete, Update Tasks",
    description: "Easily manage your tasks with intuitive controls"
  },
  {
    icon: CheckCircle2,
    title: "Mark as Complete",
    description: "Track your progress with simple completion marking"
  },
  {
    icon: Tag,
    title: "Priorities & Tags",
    description: "Organize with high/medium/low priorities and custom tags"
  },
  {
    icon: Search,
    title: "Search & Filter Tasks",
    description: "Find exactly what you need with powerful search"
  },
  {
    icon: Clock,
    title: "Sort by Date, Priority, Alphabetically",
    description: "Organize tasks in the way that works best for you"
  },
  {
    icon: Repeat,
    title: "Recurring Tasks",
    description: "Set tasks to repeat daily, weekly, or monthly"
  },
  {
    icon: Bell,
    title: "Due Dates & Reminders",
    description: "Never miss important deadlines with smart reminders"
  },
  {
    icon: MessageCircle,
    title: "AI Chatbot for Natural Language Commands",
    description: "Manage tasks using natural language commands"
  },
  {
    icon: Users,
    title: "Multi-User Support with Authentication",
    description: "Collaborate with team members securely"
  }
];

export default function FeatureSlider() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-slate-900 flex items-center justify-center">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-white mb-4">
            Powerful Features
          </h2>
          <p className="text-slate-400 max-w-[600px] mx-auto md:text-xl">
            Everything you need to boost your productivity
          </p>
        </div>

        <div className="relative overflow-hidden">
          <div className="flex animate-scroll whitespace-nowrap">
            {[...features, ...features].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={`${index}-${feature.title}`}
                  className="mx-3 flex-shrink-0 w-64 bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:bg-slate-800 transition-all duration-300"
                >
                  <div className="flex flex-col items-center text-center">
                    <div className="p-3 bg-cyan-500/10 rounded-full mb-4">
                      <Icon className="h-6 w-6 text-cyan-400" />
                    </div>
                    <h3 className="font-semibold text-white mb-2 text-sm">{feature.title}</h3>
                    <p className="text-xs text-slate-400 whitespace-normal">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-100%);
          }
        }

        .animate-scroll {
          display: flex;
          animation: scroll 40s linear infinite;
        }

        .animate-scroll:hover {
          animation-play-state: paused;
        }
      `}</style>
    </section>
  );
}