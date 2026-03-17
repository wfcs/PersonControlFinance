import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface OpenFinanceConnection {
    id: string;
    pluggy_item_id: string;
    institution_name: string;
    institution_logo_url: string | null;
    sync_status: "pending" | "success" | "failed";
    last_sync: string | null;
    next_sync: string | null;
    error_message: string | null;
    created_at: string;
    updated_at: string;
}

export interface SyncAccountsResponse {
    accounts: Array<{
        id: string;
        name: string;
        type: string;
        balance: number;
        credit_limit: number | null;
    }>;
    sync_timestamp: string;
}

export interface OpenFinanceAuthUrl {
    auth_url: string;
    code: string;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useOpenFinanceConnections() {
    return useQuery<OpenFinanceConnection[]>({
        queryKey: ["open-finance", "connections"],
        queryFn: async () => {
            const { data } = await api.get("/open_finance/connections");
            return data;
        },
    });
}

export function useOpenFinanceAuthUrl() {
    return useMutation({
        mutationFn: async () => {
            const { data } = await api.get<OpenFinanceAuthUrl>(
                "/open_finance/auth/url"
            );
            return data;
        },
    });
}

export function useConnectOpenFinance() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (code: string) => {
            const { data } = await api.post<OpenFinanceConnection>(
                "/open_finance/auth/callback",
                { code }
            );
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({
                queryKey: ["open-finance", "connections"],
            });
            qc.invalidateQueries({ queryKey: ["accounts"] });
        },
    });
}

export function useSyncOpenFinanceAccounts() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (connectionId: string) => {
            const { data } = await api.post<SyncAccountsResponse>(
                `/open_finance/sync/${connectionId}`
            );
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({
                queryKey: ["open-finance", "connections"],
            });
            qc.invalidateQueries({ queryKey: ["accounts"] });
        },
    });
}

export function useDisconnectOpenFinance() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (connectionId: string) => {
            await api.delete(`/open_finance/connections/${connectionId}`);
        },
        onSuccess: () => {
            qc.invalidateQueries({
                queryKey: ["open-finance", "connections"],
            });
            qc.invalidateQueries({ queryKey: ["accounts"] });
        },
    });
}

export function useLinkAccount() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (pluggyAccountId: string) => {
            const { data } = await api.post("/accounts/link-open-finance", {
                pluggy_account_id: pluggyAccountId,
            });
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["accounts"] });
        },
    });
}
