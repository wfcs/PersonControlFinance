"use client";

import { formatCurrency, formatPercentage } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { TrendingUp, TrendingDown, DollarSign, PiggyBank } from "lucide-react";

const SPENDING_BY_CATEGORY = [
  { name: "Moradia", value: 2100, color: "#6366f1" },
  { name: "Alimentação", value: 1250, color: "#f59e0b" },
  { name: "Transporte", value: 680, color: "#10b981" },
  { name: "Entretenimento", value: 450, color: "#ec4899" },
  { name: "Saúde", value: 320, color: "#ef4444" },
  { name: "Educação", value: 290, color: "#3b82f6" },
  { name: "Outros", value: 410, color: "#8b5cf6" },
];

const MONTHLY_COMPARISON = [
  { month: "Out/25", Receitas: 9200, Despesas: 7100 },
  { month: "Nov/25", Receitas: 8800, Despesas: 6900 },
  { month: "Dez/25", Receitas: 11500, Despesas: 9200 },
  { month: "Jan/26", Receitas: 9000, Despesas: 6800 },
  { month: "Fev/26", Receitas: 9300, Despesas: 7200 },
  { month: "Mar/26", Receitas: 9800, Despesas: 7500 },
];

const totalIncome = MONTHLY_COMPARISON.reduce((acc, d) => acc + d.Receitas, 0);
const totalExpense = MONTHLY_COMPARISON.reduce((acc, d) => acc + d.Despesas, 0);
const avgSavings = (totalIncome - totalExpense) / MONTHLY_COMPARISON.length;
const savingsRate = ((totalIncome - totalExpense) / totalIncome) * 100;
const totalSpending = SPENDING_BY_CATEGORY.reduce((acc, d) => acc + d.value, 0);

export default function ReportsPage() {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Relatórios</h1>
        <p className="text-sm text-gray-500">Análise detalhada das suas finanças</p>
      </div>

      {/* Summary stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
              <TrendingUp className="h-3.5 w-3.5 text-green-500" />
              Receita total
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-bold text-green-600">{formatCurrency(totalIncome)}</p>
            <p className="text-xs text-gray-400">últimos 6 meses</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
              <TrendingDown className="h-3.5 w-3.5 text-red-500" />
              Despesa total
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-bold text-red-600">{formatCurrency(totalExpense)}</p>
            <p className="text-xs text-gray-400">últimos 6 meses</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
              <DollarSign className="h-3.5 w-3.5 text-blue-500" />
              Economia média
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-bold">{formatCurrency(avgSavings)}</p>
            <p className="text-xs text-gray-400">por mês</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
              <PiggyBank className="h-3.5 w-3.5 text-purple-500" />
              Taxa de poupança
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-bold text-purple-600">{formatPercentage(savingsRate)}</p>
            <p className="text-xs text-gray-400">da receita total</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Donut chart: spending by category */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Gastos por Categoria (mês atual)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={SPENDING_BY_CATEGORY}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={110}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {SPENDING_BY_CATEGORY.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend
                  formatter={(value) => <span className="text-xs">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {SPENDING_BY_CATEGORY.map((cat) => (
                <div key={cat.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: cat.color }} />
                    <span className="text-gray-600">{cat.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-gray-400 text-xs">{formatPercentage((cat.value / totalSpending) * 100)}</span>
                    <span className="font-medium">{formatCurrency(cat.value)}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bar chart: income vs expense */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Receita vs Despesa (6 meses)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={MONTHLY_COMPARISON} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend />
                <Bar dataKey="Receitas" fill="#22c55e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Despesas" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {MONTHLY_COMPARISON.map((m) => {
                const saved = m.Receitas - m.Despesas;
                return (
                  <div key={m.month} className="flex items-center justify-between text-xs">
                    <span className="text-gray-500 w-14">{m.month}</span>
                    <div className="flex-1 mx-3 h-1.5 rounded-full bg-gray-100">
                      <div
                        className={`h-1.5 rounded-full ${saved >= 0 ? "bg-blue-400" : "bg-red-400"}`}
                        style={{ width: `${Math.min(Math.abs(saved / m.Receitas) * 100, 100)}%` }}
                      />
                    </div>
                    <span className={`font-medium w-20 text-right ${saved >= 0 ? "text-green-600" : "text-red-600"}`}>
                      {saved >= 0 ? "+" : ""}{formatCurrency(saved)}
                    </span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
