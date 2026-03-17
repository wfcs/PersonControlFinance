import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface BillTransaction {
    id: string;
    description: string;
    amount: number;
    date: string;
    category_id: string | null;
    type: "installment" | "recurring" | "avulsa";
}

export interface Bill {
    id: string;
    account_id: string;
    billing_month: number;
    billing_year: number;
    due_date: string;
    closing_date: string;
    total_amount: number;
    total_paid: number;
    status: "open" | "partial" | "closed" | "overdue";
    transactions: BillTransaction[];
    installments_count: number;
    recurring_count: number;
    avulsas_count: number;
}

export interface BillSummary {
    month: number;
    year: number;
    total_fixed: number;
    total_installments: number;
    total_avulsas: number;
    grand_total: number;
    bills: Bill[];
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useBills(month?: number, year?: number) {
    return useQuery<Bill[]>({
        queryKey: ["bills", month, year],
        queryFn: async () => {
            const params = new URLSearchParams();
            if (month) params.set("month", String(month));
            if (year) params.set("year", String(year));
            const { data } = await api.get(`/bills/?${params}`);
            return data;
        },
    });
}

export function useBillSummary(month: number, year: number) {
    return useQuery<BillSummary>({
        queryKey: ["bills", "summary", month, year],
        queryFn: async () => {
            const { data } = await api.get(
                `/bills/summary?month=${month}&year=${year}`
            );
            return data;
        },
    });
}

export function useBillDetail(billId: string) {
    return useQuery<Bill>({
        queryKey: ["bills", billId],
        queryFn: async () => {
            const { data } = await api.get(`/bills/${billId}`);
            return data;
        },
    });
}

export function useMarkBillAsPaid() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (billId: string) => {
            const { data } = await api.post(`/bills/${billId}/mark-paid`);
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["bills"] });
        },
    });
}
