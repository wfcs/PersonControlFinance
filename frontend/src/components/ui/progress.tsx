"use client"

import * as React from "react"
import { Progress } from "@base-ui/react/progress"

import { cn } from "@/lib/utils"

function ProgressRoot({
  className,
  value,
  ...props
}: React.ComponentProps<typeof Progress.Root>) {
  return (
    <Progress.Root
      data-slot="progress"
      value={value}
      className={cn("relative w-full", className)}
      {...props}
    >
      <Progress.Track
        className="relative h-2 w-full overflow-hidden rounded-full bg-secondary"
      >
        <Progress.Indicator
          className="h-full bg-primary transition-all duration-300 ease-in-out"
          style={{ width: `${value ?? 0}%` }}
        />
      </Progress.Track>
    </Progress.Root>
  )
}

export { ProgressRoot as Progress }
