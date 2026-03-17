import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface DashboardSummary {
    period: { year: number; month: number };
    summary: { income: number; expense: number; balance: number };
    spending_by_category: Array<{
        category_id: string | null;
        category_name: string | null;
        total: number;
    }>;
    recent_transactions: Array<Record<string, unknown>>;
}

export interface CashFlowPoint {
    year: number;
    month: number;
    income: number;
    expense: number;
    balance: number;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useDashboardSummary(year?: number, month?: number) {
    return useQuery<DashboardSummary>({
        queryKey: ["dashboard", "summary", year, month],
        queryFn: async () => {
            const params = new URLSearchParams();
            if (year) params.set("year", String(year));
            if (month) params.set("month", String(month));
            const { data } = await api.get(`/dashboard/summary?${params}`);
            return data;
        },
    });
}

export function useCashFlow(months = 6) {
    return useQuery<CashFlowPoint[]>({
        queryKey: ["dashboard", "cash-flow", months],
        queryFn: async () => {
            const { data } = await api.get(`/dashboard/cash-flow?months=${months}`);
            return data;
        },
    });
}
