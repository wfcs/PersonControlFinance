"use client";

import { useQuery } from "@tanstack/react-query";

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

const MOCK_SUMMARY: DashboardSummary = {
  totalBalance: 12540.0,
  totalIncome: 5800.0,
  totalExpenses: 3260.0,
  savingsRate: 43.8,
};

const MOCK_SPENDING: SpendingByCategory[] = [
  { category: "Alimentação", amount: 980.0, color: "#f97316", percentage: 30 },
  { category: "Moradia", amount: 1200.0, color: "#3b82f6", percentage: 36.8 },
  { category: "Transporte", amount: 420.0, color: "#8b5cf6", percentage: 12.9 },
  { category: "Saúde", amount: 260.0, color: "#10b981", percentage: 8 },
  { category: "Lazer", amount: 400.0, color: "#f59e0b", percentage: 12.3 },
];

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async (): Promise<DashboardSummary> => {
      // Mock data - replace with real API call when endpoint is available
      // const { data } = await api.get<DashboardSummary>("/dashboard/summary");
      // return data;
      return MOCK_SUMMARY;
    },
    staleTime: Infinity,
  });
}

export function useSpendingByCategory() {
  return useQuery({
    queryKey: ["dashboard", "spending-by-category"],
    queryFn: async (): Promise<SpendingByCategory[]> => {
      // Mock data - replace with real API call when endpoint is available
      // const { data } = await api.get<SpendingByCategory[]>("/dashboard/spending-by-category");
      // return data;
      return MOCK_SPENDING;
    },
    staleTime: Infinity,
  });
}
