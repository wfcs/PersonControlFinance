import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */
export interface Category {
    id: string;
    tenant_id: string;
    name: string;
    parent_id: string | null;
    icon: string | null;
    color: string | null;
    monthly_limit: number | null;
    created_at: string;
}

export interface CategoryCreate {
    name: string;
    parent_id?: string | null;
    icon?: string | null;
    color?: string | null;
    monthly_limit?: number | null;
}

export interface CategoryUpdate extends Partial<CategoryCreate> {
    id: string;
}

export interface CategoryWithStats extends Category {
    current_month_spent: number;
    percentage_used: number;
    subcategories_count: number;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useCategories() {
    return useQuery<Category[]>({
        queryKey: ["categories"],
        queryFn: async () => {
            const { data } = await api.get("/categories/");
            return data;
        },
    });
}

export function useCategoryWithStats(categoryId: string) {
    return useQuery<CategoryWithStats>({
        queryKey: ["categories", categoryId, "stats"],
        queryFn: async () => {
            const { data } = await api.get(`/categories/${categoryId}/stats`);
            return data;
        },
    });
}

export function useCreateCategory() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (body: CategoryCreate) => {
            const { data } = await api.post("/categories/", body);
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["categories"] });
        },
    });
}

export function useUpdateCategory() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (body: CategoryUpdate) => {
            const { id, ...payload } = body;
            const { data } = await api.put(`/categories/${id}`, payload);
            return data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["categories"] });
        },
    });
}

export function useDeleteCategory() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (id: string) => {
            await api.delete(`/categories/${id}`);
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["categories"] });
        },
    });
}
