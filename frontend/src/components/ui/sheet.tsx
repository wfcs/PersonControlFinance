"use client"

import * as React from "react"
import { Dialog } from "@base-ui/react/dialog"
import { cva, type VariantProps } from "class-variance-authority"
import { X } from "lucide-react"

import { cn } from "@/lib/utils"

const Sheet = Dialog.Root

const SheetTrigger = Dialog.Trigger

const SheetClose = Dialog.Close

const SheetPortal = Dialog.Portal

function SheetBackdrop({ className, ...props }: React.ComponentProps<typeof Dialog.Backdrop>) {
  return (
    <Dialog.Backdrop
      className={cn(
        "fixed inset-0 z-50 bg-black/80",
        "data-[ending-style]:opacity-0 data-[starting-style]:opacity-0 transition-opacity duration-300",
        className
      )}
      {...props}
    />
  )
}

const sheetVariants = cva(
  "fixed z-50 gap-4 bg-background p-6 shadow-lg transition-transform duration-300 ease-in-out",
  {
    variants: {
      side: {
        top: "inset-x-0 top-0 border-b data-[ending-style]:-translate-y-full data-[starting-style]:-translate-y-full",
        bottom:
          "inset-x-0 bottom-0 border-t data-[ending-style]:translate-y-full data-[starting-style]:translate-y-full",
        left: "inset-y-0 left-0 h-full w-3/4 border-r data-[ending-style]:-translate-x-full data-[starting-style]:-translate-x-full sm:max-w-sm",
        right:
          "inset-y-0 right-0 h-full w-3/4 border-l data-[ending-style]:translate-x-full data-[starting-style]:translate-x-full sm:max-w-sm",
      },
    },
    defaultVariants: {
      side: "right",
    },
  }
)

interface SheetContentProps
  extends React.ComponentProps<typeof Dialog.Popup>,
    VariantProps<typeof sheetVariants> {}

function SheetContent({ side = "right", className, children, ...props }: SheetContentProps) {
  return (
    <Dialog.Portal>
      <SheetBackdrop />
      <Dialog.Popup
        data-slot="sheet-content"
        className={cn(sheetVariants({ side }), className)}
        {...props}
      >
        {children}
        <Dialog.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none">
          <X className="size-4" />
          <span className="sr-only">Close</span>
        </Dialog.Close>
      </Dialog.Popup>
    </Dialog.Portal>
  )
}

function SheetHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="sheet-header"
      className={cn("flex flex-col gap-2 text-left", className)}
      {...props}
    />
  )
}

function SheetFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="sheet-footer"
      className={cn("flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", className)}
      {...props}
    />
  )
}

function SheetTitle({ className, ...props }: React.ComponentProps<typeof Dialog.Title>) {
  return (
    <Dialog.Title
      data-slot="sheet-title"
      className={cn("text-lg font-semibold text-foreground", className)}
      {...props}
    />
  )
}

function SheetDescription({ className, ...props }: React.ComponentProps<typeof Dialog.Description>) {
  return (
    <Dialog.Description
      data-slot="sheet-description"
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
}

export {
  Sheet,
  SheetTrigger,
  SheetClose,
  SheetPortal,
  SheetBackdrop,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription,
}
