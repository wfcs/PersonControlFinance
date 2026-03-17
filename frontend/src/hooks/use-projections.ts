import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface BalanceProjection {
    month: string;
    year: number;
    month_number: number;
    projected_balance: number;
    income: number;
    expenses: number;
    confidence: number;
}

export interface ProjectionSummary {
    current_balance: number;
    projections: BalanceProjection[];
    warnings: Array<{
        month: string;
        type: "negative_balance" | "low_balance";
        message: string;
    }>;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useBalanceProjection(months: number = 6) {
    return useQuery<ProjectionSummary>({
        queryKey: ["projections", "balance", months],
        queryFn: async () => {
            const { data } = await api.get(`/projections/balance?months=${months}`);
            return data;
        },
    });
}

export function useExpenseProjection(months: number = 12) {
    return useQuery<BalanceProjection[]>({
        queryKey: ["projections", "expenses", months],
        queryFn: async () => {
            const { data } = await api.get(`/projections/expenses?months=${months}`);
            return data;
        },
    });
}

export function useIncomeProjection(months: number = 12) {
    return useQuery<BalanceProjection[]>({
        queryKey: ["projections", "income", months],
        queryFn: async () => {
            const { data } = await api.get(`/projections/income?months=${months}`);
            return data;
        },
    });
}
