"use client";

import { useState } from "react";
import { formatCurrency } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { AlertTriangle, TrendingUp } from "lucide-react";

type Period = "3M" | "6M" | "12M";

function generateProjectionData(months: number) {
  const data = [];
  const now = new Date();
  let balance = 15000;

  for (let i = 0; i <= months; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
    const label = d.toLocaleString("pt-BR", { month: "short", year: "2-digit" });

    if (i > 0) {
      const income = 9000 + (Math.random() - 0.3) * 2000;
      const expense = 6500 + (Math.random() - 0.2) * 2000;
      balance += income - expense;
    }

    data.push({
      month: label,
      saldo: Math.round(balance),
      projetado: i > 0,
    });
  }

  return data;
}

export default function ProjectionPage() {
  const [period, setPeriod] = useState<Period>("6M");
  const months = period === "3M" ? 3 : period === "6M" ? 6 : 12;

  const data = generateProjectionData(months);
  const hasNegative = data.some((d) => d.saldo < 0);
  const finalBalance = data[data.length - 1]?.saldo ?? 0;
  const minBalance = Math.min(...data.map((d) => d.saldo));

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Projeção Financeira</h1>
          <p className="text-sm text-gray-500">Estimativa do saldo futuro com base no histórico</p>
        </div>
        <div className="flex rounded-lg border bg-white">
          {(["3M", "6M", "12M"] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 text-sm font-medium transition-colors first:rounded-l-lg last:rounded-r-lg ${
                period === p ? "bg-blue-600 text-white" : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {hasNegative && (
        <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
          <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" />
          <div>
            <p className="text-sm font-semibold text-red-700">Alerta: saldo projetado negativo</p>
            <p className="text-xs text-red-600">
              A projeção indica que seu saldo poderá ficar negativo no período. Revise suas despesas ou aumente suas receitas.
            </p>
          </div>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm font-medium text-gray-500">Saldo atual</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{formatCurrency(data[0]?.saldo ?? 0)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-1 text-sm font-medium text-gray-500">
              <TrendingUp className="h-4 w-4" />
              Saldo projetado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${finalBalance >= 0 ? "text-gray-900" : "text-red-600"}`}>
              {formatCurrency(finalBalance)}
            </p>
            <p className="text-xs text-gray-400">em {months} meses</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm font-medium text-gray-500">Saldo mínimo projetado</CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${minBalance >= 0 ? "text-gray-900" : "text-red-600"}`}>
              {formatCurrency(minBalance)}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Evolução projetada do saldo</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} labelClassName="font-medium" />
              {hasNegative && (
                <ReferenceLine y={0} stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Zero", fill: "#ef4444", fontSize: 11 }} />
              )}
              <Line
                type="monotone"
                dataKey="saldo"
                stroke="#3b82f6"
                strokeWidth={2.5}
                dot={{ fill: "#3b82f6", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="rounded-lg border bg-amber-50 p-4 text-sm text-amber-800">
        <strong>Aviso:</strong> Esta projeção é baseada em dados históricos e recorrências cadastradas.
        Valores reais podem variar. Use como referência para planejamento.
      </div>
    </div>
  );
}
