import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface Transaction {
    id: string;
    account_id: string;
    category_id: string | null;
    description: string;
    amount: number;
    type: string;
    date: string;
    notes: string | null;
    is_excluded: boolean;
    installment_number: number | null;
    installment_total: number | null;
    created_at: string;
}

export interface TransactionListResponse {
    items: Transaction[];
    total: number;
    page: number;
    page_size: number;
}

export interface TransactionFilters {
    account_id?: string;
    category_id?: string;
    type?: string;
    date_from?: string;
    date_to?: string;
    search?: string;
    page?: number;
    page_size?: number;
}

export interface TransactionCreate {
    account_id: string;
    category_id?: string | null;
    description: string;
    amount: number;
    type: string;
    date: string;
    notes?: string | null;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useTransactions(filters: TransactionFilters = {}) {
    return useQuery<TransactionListResponse>({
        queryKey: ["transactions", filters],
        queryFn: async () => {
            const params = new URLSearchParams();
            Object.entries(filters).forEach(([k, v]) => {
                if (v !== undefined && v !== null && v !== "") params.set(k, String(v));
            });
            const { data } = await api.get(`/transactions/?${params}`);
            return data;
        },
    });
}

export function useCreateTransaction() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (body: TransactionCreate) => {
            const { data } = await api.post("/transactions/", body);
            return data;
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: ["transactions"] }),
    });
}

export function useDeleteTransaction() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (id: string) => {
            await api.delete(`/transactions/${id}`);
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: ["transactions"] }),
    });
}
