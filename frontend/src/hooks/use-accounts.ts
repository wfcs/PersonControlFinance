import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface Account {
    id: string;
    name: string;
    institution_name: string;
    institution_logo_url: string | null;
    type: string;
    balance: number;
    credit_limit: number | null;
    is_active: boolean;
    pluggy_item_id: string | null;
    created_at: string;
}

export interface AccountCreate {
    name: string;
    institution_name: string;
    type: string;
    balance?: number;
    credit_limit?: number | null;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useAccounts() {
    return useQuery<Account[]>({
        queryKey: ["accounts"],
        queryFn: async () => {
            const { data } = await api.get("/accounts/");
            return data;
        },
    });
}

export function useCreateAccount() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (body: AccountCreate) => {
            const { data } = await api.post("/accounts/", body);
            return data;
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
    });
}

export function useDeleteAccount() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (id: string) => {
            await api.delete(`/accounts/${id}`);
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
    });
}
