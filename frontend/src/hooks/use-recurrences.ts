import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface Recurrence {
    id: string;
    account_id: string;
    category_id: string | null;
    name: string;
    description: string | null;
    amount: number;
    frequency: "daily" | "weekly" | "biweekly" | "monthly" | "quarterly" | "annual";
    next_occurrence: string;
    last_occurrence: string | null;
    is_active: boolean;
    is_auto_detected: boolean;
    confidence_score: number;
    created_at: string;
}

export interface RecurrenceCreate {
    account_id: string;
    category_id?: string | null;
    name: string;
    description?: string | null;
    amount: number;
    frequency: Recurrence["frequency"];
    next_occurrence: string;
}

export interface RecurrenceUpdate extends Partial<RecurrenceCreate> {
    id: string;
}

export interface RecurrenceMonthly {
    month: string;
    year: number;
    fixed_expenses: number;
    estimated_installments: number;
    total_expected: number;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useRecurrences() {
    return useQuery<Recurrence[]>({
        queryKey: ["recurrences"],
        queryFn: async () => {
            const { data } = await api.get("/recurrences/");
            return data;
        },
    });
}

export function useRecurrencesByMonth(year: number, month: number) {
    return useQuery<RecurrenceMonthly>({
        queryKey: ["recurrences", "month", year, month],
        queryFn: async () => {
            const { data } = await api.get(
                `/recurrences/month?year=${year}&month=${month}`
            );
            return data;
        },
    });
}

export function useCreateRecurrence() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (body: RecurrenceCreate) => {
            const { data } = await api.post("/recurrences/", body);
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["recurrences"] });
        },
    });
}

export function useUpdateRecurrence() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (body: RecurrenceUpdate) => {
            const { id, ...payload } = body;
            const { data } = await api.put(`/recurrences/${id}`, payload);
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["recurrences"] });
        },
    });
}

export function useDeleteRecurrence() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (id: string) => {
            await api.delete(`/recurrences/${id}`);
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["recurrences"] });
        },
    });
}

export function useDetectRecurrences() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (accountId: string) => {
            const { data } = await api.post(
                `/recurrences/detect?account_id=${accountId}`
            );
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["recurrences"] });
        },
    });
}
