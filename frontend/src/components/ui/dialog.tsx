"use client"

import * as React from "react"
import { Dialog } from "@base-ui/react/dialog"

import { cn } from "@/lib/utils"

const DialogRoot = Dialog.Root

const DialogTrigger = Dialog.Trigger

const DialogPortal = Dialog.Portal

const DialogClose = Dialog.Close

function DialogBackdrop({ className, ...props }: React.ComponentProps<typeof Dialog.Backdrop>) {
  return (
    <Dialog.Backdrop
      className={cn(
        "fixed inset-0 z-50 bg-black/80",
        "data-[ending-style]:opacity-0 data-[starting-style]:opacity-0 transition-opacity duration-200",
        className
      )}
      {...props}
    />
  )
}

function DialogPopup({ className, ...props }: React.ComponentProps<typeof Dialog.Popup>) {
  return (
    <Dialog.Popup
      className={cn(
        "fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2",
        "rounded-xl border border-border bg-background p-6 shadow-lg",
        "data-[ending-style]:opacity-0 data-[ending-style]:scale-95",
        "data-[starting-style]:opacity-0 data-[starting-style]:scale-95",
        "transition-[opacity,transform] duration-200",
        className
      )}
      {...props}
    />
  )
}

function DialogTitle({ className, ...props }: React.ComponentProps<typeof Dialog.Title>) {
  return (
    <Dialog.Title
      className={cn("text-lg font-semibold leading-none tracking-tight", className)}
      {...props}
    />
  )
}

function DialogDescription({ className, ...props }: React.ComponentProps<typeof Dialog.Description>) {
  return (
    <Dialog.Description
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
}

function DialogHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex flex-col gap-2 text-center sm:text-left", className)}
      {...props}
    />
  )
}

function DialogFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", className)}
      {...props}
    />
  )
}

export {
  DialogRoot as Dialog,
  DialogTrigger,
  DialogPortal,
  DialogClose,
  DialogBackdrop,
  DialogPopup,
  DialogPopup as DialogContent,
  DialogTitle,
  DialogDescription,
  DialogHeader,
  DialogFooter,
}
