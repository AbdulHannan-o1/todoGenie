'use client';

import Link from 'next/link';
import { Twitter, Github, Linkedin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="w-full border-t border-slate-800 bg-slate-950">
      <div className="container px-4 md:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Column */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">TodoGenie</h3>
            <p className="text-sm text-slate-400">
              AI-Native Todo Management for modern productivity
            </p>
            <div className="flex space-x-4">
              <Link href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">
                <Twitter className="h-5 w-5" />
                <span className="sr-only">Twitter</span>
              </Link>
              <Link href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">
                <Github className="h-5 w-5" />
                <span className="sr-only">GitHub</span>
              </Link>
              <Link href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">
                <Linkedin className="h-5 w-5" />
                <span className="sr-only">LinkedIn</span>
              </Link>
            </div>
          </div>

          {/* Quick Links Column */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources Column */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  GitHub Repo
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  API Docs
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Support
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal Column */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Security
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-slate-400">
            © 2025 TodoGenie. Built for Hackathon II.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
              Privacy Policy
            </Link>
            <Link href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}