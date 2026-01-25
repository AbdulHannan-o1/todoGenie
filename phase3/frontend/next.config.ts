import type { NextConfig } from "next";

const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' blob: data:;
  media-src 'none';
  connect-src 'self' http://localhost:8000;
  font-src 'self';
`;

const securityHeaders = [
  {
    key: "X-DNS-Prefetch-Control",
    value: "on",
  },
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains; preload",
  },
  {
    key: "X-XSS-Protection",
    value: "1; mode=block",
  },
  {
    key: "X-Frame-Options",
    value: "SAMEORIGIN",
  },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
  {
    key: "X-Content-Type-Options",
    value: "nosniff",
  },
  {
    key: "Referrer-Policy",
    value: "origin-when-cross-origin",
  },
  {
    key: "Content-Security-Policy",
    value: ContentSecurityPolicy.replace(/\s{2,}/g, " ").trim(),
  },
];

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: "/api/:user_id/tasks/:path*",
        destination: `http://localhost:8000/api/:user_id/tasks/:path*`,
      },
      {
        source: "/api/v1/chat/:path*",
        destination: `http://localhost:8000/api/v1/chat/:path*`,
      },
      {
        source: "/api/v1/voice/:path*",
        destination: `http://localhost:8000/api/v1/voice/:path*`,
      },
      {
        source: "/api/auth/:path*",
        destination: `http://localhost:8000/api/auth/:path*`,
      },
      {
        source: "/auth/:path*",
        destination: `http://localhost:8000/auth/:path*`,
      },
      {
        source: "/api/tasks/:path*",
        destination: `http://localhost:8000/api/tasks/:path*`,
      },
      {
        source: "/:user_id/tasks/:path*",
        destination: `http://localhost:8000/api/:user_id/tasks/:path*`,
      },
      {
        source: "/api/users/:path*",
        destination: `http://localhost:8000/api/users/:path*`,
      },
      {
        source: "/users/:path*",
        destination: `http://localhost:8000/api/users/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: securityHeaders,
      },
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Credentials", value: "true" },
          { key: "Access-Control-Allow-Origin", value: "*" },
          { key: "Access-Control-Allow-Methods", value: "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
          { key: "Access-Control-Allow-Headers", value: "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization" },
        ],
      },
    ];
  },
};

export default nextConfig;