"use client";

import { useState } from "react";
import { formatCurrency } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { TrendingUp, TrendingDown, DollarSign } from "lucide-react";

type Period = "3M" | "6M" | "12M";

function generateMockData(months: number) {
  const data = [];
  const now = new Date();
  for (let i = months - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const monthLabel = d.toLocaleString("pt-BR", { month: "short", year: "2-digit" });
    const income = 7000 + Math.random() * 4000;
    const expense = 4000 + Math.random() * 3000;
    data.push({
      month: monthLabel,
      Receitas: Math.round(income),
      Despesas: Math.round(expense),
      Resultado: Math.round(income - expense),
    });
  }
  return data;
}

export default function CashFlowPage() {
  const [period, setPeriod] = useState<Period>("6M");

  const months = period === "3M" ? 3 : period === "6M" ? 6 : 12;
  const data = generateMockData(months);

  const totalIncome = data.reduce((acc, d) => acc + d.Receitas, 0);
  const totalExpense = data.reduce((acc, d) => acc + d.Despesas, 0);
  const netResult = totalIncome - totalExpense;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Fluxo de Caixa</h1>
          <p className="text-sm text-gray-500">Visão geral de entradas e saídas no período</p>
        </div>
        <div className="flex rounded-lg border bg-white">
          {(["3M", "6M", "12M"] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 text-sm font-medium transition-colors first:rounded-l-lg last:rounded-r-lg ${
                period === p
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <TrendingUp className="h-4 w-4 text-green-500" />
              Total Receitas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(totalIncome)}</p>
            <p className="text-xs text-gray-400">Últimos {months} meses</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <TrendingDown className="h-4 w-4 text-red-500" />
              Total Despesas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">{formatCurrency(totalExpense)}</p>
            <p className="text-xs text-gray-400">Últimos {months} meses</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <DollarSign className="h-4 w-4 text-blue-500" />
              Resultado Líquido
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${netResult >= 0 ? "text-gray-900" : "text-red-600"}`}>
              {formatCurrency(netResult)}
            </p>
            <p className="text-xs text-gray-400">
              {netResult >= 0 ? "Saldo positivo" : "Saldo negativo"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Stacked bar chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Receitas vs Despesas por Mês</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Legend />
              <Bar dataKey="Receitas" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Despesas" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Monthly breakdown table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Detalhamento Mensal</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="pb-2 font-medium">Mês</th>
                  <th className="pb-2 text-right font-medium text-green-600">Receitas</th>
                  <th className="pb-2 text-right font-medium text-red-600">Despesas</th>
                  <th className="pb-2 text-right font-medium">Resultado</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data.map((row) => (
                  <tr key={row.month}>
                    <td className="py-2 capitalize">{row.month}</td>
                    <td className="py-2 text-right text-green-600">{formatCurrency(row.Receitas)}</td>
                    <td className="py-2 text-right text-red-600">{formatCurrency(row.Despesas)}</td>
                    <td className={`py-2 text-right font-medium ${row.Resultado >= 0 ? "text-gray-900" : "text-red-600"}`}>
                      {formatCurrency(row.Resultado)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
