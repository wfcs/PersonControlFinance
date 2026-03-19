"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export interface Transaction {
  id: string;
  description: string;
  amount: number;
  type: "income" | "expense" | "transfer";
  date: string;
  account_id: string;
  category_id?: string;
  notes?: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionFilters {
  account_id?: string;
  category_id?: string;
  type?: "income" | "expense" | "transfer";
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
}

export interface CreateTransactionPayload {
  description: string;
  amount: number;
  type: "income" | "expense" | "transfer";
  date: string;
  account_id: string;
  category_id?: string;
  notes?: string;
}

export interface UpdateTransactionPayload
  extends Partial<CreateTransactionPayload> {}

const TRANSACTIONS_KEY = ["transactions"] as const;

export function useTransactions(filters?: TransactionFilters) {
  return useQuery({
    queryKey: [...TRANSACTIONS_KEY, filters],
    queryFn: async () => {
      const { data } = await api.get<Transaction[]>("/transactions", {
        params: filters,
      });
      return data;
    },
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: CreateTransactionPayload) => {
      const { data } = await api.post<Transaction>("/transactions", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY });
    },
  });
}

export function useUpdateTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...payload
    }: UpdateTransactionPayload & { id: string }) => {
      const { data } = await api.patch<Transaction>(
        `/transactions/${id}`,
        payload
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY });
    },
  });
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/transactions/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY });
    },
  });
}
