import { format, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";

export function formatCurrency(value: number | string): string {
    const num = typeof value === "string" ? parseFloat(value) : value;
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(num);
}

export function formatDate(date: string | Date, pattern = "dd/MM/yyyy"): string {
    const d = typeof date === "string" ? parseISO(date) : date;
    return format(d, pattern, { locale: ptBR });
}

export function formatDateTime(date: string | Date): string {
    return formatDate(date, "dd/MM/yyyy HH:mm");
}

export function formatMonthYear(date: string | Date): string {
    return formatDate(date, "MMM yyyy");
}

export function classifyAmount(amount: number): "income" | "expense" {
    return amount >= 0 ? "income" : "expense";
}
