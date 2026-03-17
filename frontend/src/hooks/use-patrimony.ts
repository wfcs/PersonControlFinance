import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface Asset {
    id: string;
    name: string;
    type: string;
    value: number;
    description: string | null;
}

export interface Liability {
    id: string;
    name: string;
    type: string;
    value: number;
    description: string | null;
}

export interface PatrimonySnapshot {
    date: string;
    total_assets: number;
    total_liabilities: number;
    net_worth: number;
    assets: Asset[];
    liabilities: Liability[];
}

export interface PatrimonyHistory {
    date: string;
    net_worth: number;
    total_assets: number;
    total_liabilities: number;
    variation_percentage: number;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function usePatrimonySnapshot() {
    return useQuery<PatrimonySnapshot>({
        queryKey: ["patrimony", "current"],
        queryFn: async () => {
            const { data } = await api.get("/patrimony/");
            return data;
        },
    });
}

export function usePatrimonyHistory(months = 12) {
    return useQuery<PatrimonyHistory[]>({
        queryKey: ["patrimony", "history", months],
        queryFn: async () => {
            const { data } = await api.get(`/patrimony/history?months=${months}`);
            return data;
        },
    });
}

export function usePatrimonyProjection(months = 12) {
    return useQuery<PatrimonyHistory[]>({
        queryKey: ["patrimony", "projection", months],
        queryFn: async () => {
            const { data } = await api.get(`/patrimony/projection?months=${months}`);
            return data;
        },
    });
}
