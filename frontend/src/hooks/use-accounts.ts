"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export interface Account {
  id: string;
  name: string;
  type: string;
  balance: number;
  currency: string;
  is_active: boolean;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateAccountPayload {
  name: string;
  type: string;
  balance?: number;
  currency?: string;
}

export interface UpdateAccountPayload extends Partial<CreateAccountPayload> {
  is_active?: boolean;
}

const ACCOUNTS_KEY = ["accounts"] as const;

export function useAccounts() {
  return useQuery({
    queryKey: ACCOUNTS_KEY,
    queryFn: async () => {
      const { data } = await api.get<Account[]>("/accounts");
      return data;
    },
  });
}

export function useCreateAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: CreateAccountPayload) => {
      const { data } = await api.post<Account>("/accounts", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ACCOUNTS_KEY });
    },
  });
}

export function useUpdateAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...payload
    }: UpdateAccountPayload & { id: string }) => {
      const { data } = await api.patch<Account>(`/accounts/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ACCOUNTS_KEY });
    },
  });
}

export function useDeleteAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/accounts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ACCOUNTS_KEY });
    },
  });
}
