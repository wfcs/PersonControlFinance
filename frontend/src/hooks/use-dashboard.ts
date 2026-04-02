"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export interface DashboardSummary {
  totalBalance: number;
  totalIncome: number;
  totalExpenses: number;
  savingsRate: number;
}

export interface SpendingByCategory {
  category: string;
  amount: number;
  color: string;
  percentage: number;
}

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async (): Promise<DashboardSummary> => {
      const { data } = await api.get<DashboardSummary>("/dashboard/summary");
      return data;
    },
  });
}

export function useSpendingByCategory() {
  return useQuery({
    queryKey: ["dashboard", "spending-by-category"],
    queryFn: async (): Promise<SpendingByCategory[]> => {
      const { data } = await api.get<SpendingByCategory[]>("/dashboard/spending-by-category");
      return data;
    },
  });
}
