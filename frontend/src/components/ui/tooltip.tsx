"use client"

import * as React from "react"
import { Tooltip } from "@base-ui/react/tooltip"

import { cn } from "@/lib/utils"

const TooltipProvider = Tooltip.Provider

const TooltipRoot = Tooltip.Root

const TooltipTrigger = Tooltip.Trigger

function TooltipContent({
  className,
  sideOffset = 4,
  ...props
}: React.ComponentProps<typeof Tooltip.Popup> & { sideOffset?: number }) {
  return (
    <Tooltip.Portal>
      <Tooltip.Positioner sideOffset={sideOffset}>
        <Tooltip.Popup
          data-slot="tooltip-content"
          className={cn(
            "z-50 overflow-hidden rounded-md bg-popover px-3 py-1.5 text-xs text-popover-foreground shadow-md",
            "data-[ending-style]:opacity-0 data-[starting-style]:opacity-0",
            "transition-opacity duration-150",
            className
          )}
          {...props}
        />
      </Tooltip.Positioner>
    </Tooltip.Portal>
  )
}

export { TooltipProvider, TooltipRoot as Tooltip, TooltipTrigger, TooltipContent }
