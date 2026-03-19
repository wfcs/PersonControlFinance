"use client";

import { cn } from "@/lib/utils";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  variant?: "full" | "icon";
  className?: string;
}

export function Logo({ size = "md", variant = "full", className }: LogoProps) {
  const sizes = {
    sm: { icon: 28, text: "text-base" },
    md: { icon: 34, text: "text-lg" },
    lg: { icon: 48, text: "text-2xl" },
  };

  const { icon, text } = sizes[size];

  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg
        width={icon}
        height={icon}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0"
      >
        {/* Rounded square background */}
        <rect width="48" height="48" rx="12" fill="url(#brand-gradient)" />

        {/* Stylized "F" with upward arrow — finance + growth */}
        <path
          d="M16 36V16.5C16 15.12 17.12 14 18.5 14H30"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M16 25H26"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
        />

        {/* Upward arrow — growth indicator */}
        <path
          d="M28 30L33 20L38 30"
          stroke="#A7F3D0"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M33 20V18"
          stroke="#A7F3D0"
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        <defs>
          <linearGradient
            id="brand-gradient"
            x1="0"
            y1="0"
            x2="48"
            y2="48"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#059669" />
            <stop offset="1" stopColor="#0D9488" />
          </linearGradient>
        </defs>
      </svg>

      {variant === "full" && (
        <span
          className={cn(
            text,
            "font-bold tracking-tight"
          )}
          style={{ fontFamily: "var(--font-heading)" }}
        >
          Fin<span className="text-brand-500">Control</span>
        </span>
      )}
    </div>
  );
}
