import { format, parseISO } from "date-fns"

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value)
}

export function formatDate(date: string | Date): string {
  const parsed = typeof date === "string" ? parseISO(date) : date
  return format(parsed, "dd/MM/yyyy")
}

export function formatDateTime(date: string | Date): string {
  const parsed = typeof date === "string" ? parseISO(date) : date
  return format(parsed, "dd/MM/yyyy HH:mm")
}
