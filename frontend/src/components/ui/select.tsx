"use client"

import * as React from "react"
import { ChevronDown } from "lucide-react"

import { cn } from "@/lib/utils"

const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => {
  return (
    <div className="relative w-full">
      <select
        ref={ref}
        data-slot="select"
        className={cn(
          "flex h-9 w-full appearance-none rounded-lg border border-input bg-background px-3 py-1 pr-8 text-sm shadow-sm transition-colors",
          "focus-visible:outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-invalid:border-destructive",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
    </div>
  )
})
Select.displayName = "Select"

function SelectItem({
  className,
  children,
  ...props
}: React.OptionHTMLAttributes<HTMLOptionElement>) {
  return (
    <option className={cn(className)} {...props}>
      {children}
    </option>
  )
}

function SelectGroup({
  className,
  children,
  label,
  ...props
}: React.OptgroupHTMLAttributes<HTMLOptGroupElement> & { label?: string }) {
  return (
    <optgroup label={label} className={cn(className)} {...props}>
      {children}
    </optgroup>
  )
}

// Aliases for shadcn-style imports used by pages
const SelectTrigger = Select
const SelectContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ children, ...props }, ref) => <div ref={ref} {...props}>{children}</div>
)
SelectContent.displayName = "SelectContent"

function SelectValue({ placeholder }: { placeholder?: string }) {
  return null // native select handles value display
}

export { Select, SelectItem, SelectGroup, SelectTrigger, SelectContent, SelectValue }
