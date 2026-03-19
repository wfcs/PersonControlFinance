"use client"

import * as React from "react"
import { Popover } from "@base-ui/react/popover"

import { cn } from "@/lib/utils"

const PopoverRoot = Popover.Root

const PopoverTrigger = Popover.Trigger

const PopoverPortal = Popover.Portal

const PopoverClose = Popover.Close

function PopoverBackdrop({ className, ...props }: React.ComponentProps<typeof Popover.Backdrop>) {
  return (
    <Popover.Backdrop
      className={cn("fixed inset-0 z-50", className)}
      {...props}
    />
  )
}

function PopoverContent({
  className,
  align = "center",
  sideOffset = 4,
  ...props
}: React.ComponentProps<typeof Popover.Popup> & {
  align?: "start" | "center" | "end"
  sideOffset?: number
}) {
  return (
    <Popover.Portal>
      <Popover.Positioner sideOffset={sideOffset} align={align}>
        <Popover.Popup
          data-slot="popover-content"
          className={cn(
            "z-50 w-72 rounded-xl border border-border bg-popover p-4 text-popover-foreground shadow-md outline-none",
            "data-[ending-style]:opacity-0 data-[starting-style]:opacity-0",
            "transition-opacity duration-150",
            className
          )}
          {...props}
        />
      </Popover.Positioner>
    </Popover.Portal>
  )
}

function PopoverTitle({ className, ...props }: React.ComponentProps<typeof Popover.Title>) {
  return (
    <Popover.Title
      className={cn("mb-1 font-semibold leading-none tracking-tight", className)}
      {...props}
    />
  )
}

function PopoverDescription({ className, ...props }: React.ComponentProps<typeof Popover.Description>) {
  return (
    <Popover.Description
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
}

export {
  PopoverRoot as Popover,
  PopoverTrigger,
  PopoverPortal,
  PopoverClose,
  PopoverBackdrop,
  PopoverContent,
  PopoverTitle,
  PopoverDescription,
}
