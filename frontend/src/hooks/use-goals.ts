"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export interface Goal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline?: string;
  description?: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateGoalPayload {
  name: string;
  target_amount: number;
  current_amount?: number;
  deadline?: string;
  description?: string;
}

export interface UpdateGoalPayload extends Partial<CreateGoalPayload> {}

const GOALS_KEY = ["goals"] as const;

export function useGoals() {
  return useQuery({
    queryKey: GOALS_KEY,
    queryFn: async () => {
      const { data } = await api.get<Goal[]>("/goals");
      return data;
    },
  });
}

export function useCreateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: CreateGoalPayload) => {
      const { data } = await api.post<Goal>("/goals", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GOALS_KEY });
    },
  });
}

export function useUpdateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...payload
    }: UpdateGoalPayload & { id: string }) => {
      const { data } = await api.patch<Goal>(`/goals/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GOALS_KEY });
    },
  });
}

export function useDeleteGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/goals/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GOALS_KEY });
    },
  });
}
