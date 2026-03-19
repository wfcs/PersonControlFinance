"use client";

import { formatCurrency, formatDate } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { RefreshCw } from "lucide-react";

interface Recurrence {
  id: string;
  description: string;
  amount: number;
  type: "income" | "expense";
  frequency: "mensal" | "semanal" | "quinzenal" | "anual";
  next_due: string;
  category: string;
}

const MOCK_RECURRENCES: Recurrence[] = [
  { id: "1", description: "Aluguel", amount: 1800, type: "expense", frequency: "mensal", next_due: "2026-04-05", category: "Moradia" },
  { id: "2", description: "Netflix", amount: 55.9, type: "expense", frequency: "mensal", next_due: "2026-04-10", category: "Entretenimento" },
  { id: "3", description: "Spotify", amount: 21.9, type: "expense", frequency: "mensal", next_due: "2026-04-15", category: "Entretenimento" },
  { id: "4", description: "Salário", amount: 8500, type: "income", frequency: "mensal", next_due: "2026-04-01", category: "Renda" },
  { id: "5", description: "Freelance mensal", amount: 2000, type: "income", frequency: "mensal", next_due: "2026-04-20", category: "Renda" },
  { id: "6", description: "Academia", amount: 99, type: "expense", frequency: "mensal", next_due: "2026-04-08", category: "Saúde" },
  { id: "7", description: "Internet", amount: 110, type: "expense", frequency: "mensal", next_due: "2026-04-12", category: "Contas" },
  { id: "8", description: "Seguro de vida", amount: 350, type: "expense", frequency: "anual", next_due: "2026-11-01", category: "Seguros" },
];

const MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

function buildAnnualChart(recurrences: Recurrence[]) {
  return MONTHS.map((month) => {
    const income = recurrences
      .filter((r) => r.type === "income" && (r.frequency === "mensal" || r.frequency === "quinzenal" || r.frequency === "semanal"))
      .reduce((acc, r) => {
        if (r.frequency === "semanal") return acc + r.amount * 4;
        if (r.frequency === "quinzenal") return acc + r.amount * 2;
        return acc + r.amount;
      }, 0);
    const expense = recurrences
      .filter((r) => r.type === "expense" && (r.frequency === "mensal" || r.frequency === "quinzenal" || r.frequency === "semanal"))
      .reduce((acc, r) => {
        if (r.frequency === "semanal") return acc + r.amount * 4;
        if (r.frequency === "quinzenal") return acc + r.amount * 2;
        return acc + r.amount;
      }, 0);
    return { month, Receitas: income, Despesas: expense };
  });
}

const FREQUENCY_LABELS: Record<string, string> = {
  mensal: "Mensal",
  semanal: "Semanal",
  quinzenal: "Quinzenal",
  anual: "Anual",
};

const FREQUENCY_COLORS: Record<string, string> = {
  mensal: "bg-blue-100 text-blue-700",
  semanal: "bg-purple-100 text-purple-700",
  quinzenal: "bg-orange-100 text-orange-700",
  anual: "bg-gray-100 text-gray-700",
};

export default function RecurringPage() {
  const chartData = buildAnnualChart(MOCK_RECURRENCES);
  const totalMonthlyIncome = MOCK_RECURRENCES.filter((r) => r.type === "income" && r.frequency === "mensal").reduce((acc, r) => acc + r.amount, 0);
  const totalMonthlyExpense = MOCK_RECURRENCES.filter((r) => r.type === "expense" && r.frequency === "mensal").reduce((acc, r) => acc + r.amount, 0);

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Recorrências</h1>
        <p className="text-sm text-gray-500">Receitas e despesas que se repetem periodicamente</p>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm font-medium text-gray-500">Receitas mensais</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(totalMonthlyIncome)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm font-medium text-gray-500">Despesas mensais</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">{formatCurrency(totalMonthlyExpense)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm font-medium text-gray-500">Resultado mensal</CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${totalMonthlyIncome - totalMonthlyExpense >= 0 ? "text-gray-900" : "text-red-600"}`}>
              {formatCurrency(totalMonthlyIncome - totalMonthlyExpense)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* List */}
      {MOCK_RECURRENCES.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-20 text-center">
          <RefreshCw className="mb-4 h-12 w-12 text-gray-300" />
          <h3 className="text-base font-semibold text-gray-700">Nenhuma recorrência</h3>
          <p className="text-sm text-gray-400">As transações recorrentes aparecerão aqui</p>
        </div>
      ) : (
        <div className="space-y-2">
          <h2 className="text-base font-semibold">Lançamentos recorrentes</h2>
          <div className="divide-y rounded-lg border bg-white">
            {MOCK_RECURRENCES.map((r) => (
              <div key={r.id} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className={`flex h-9 w-9 items-center justify-center rounded-full ${r.type === "income" ? "bg-green-100" : "bg-red-100"}`}>
                    <RefreshCw className={`h-4 w-4 ${r.type === "income" ? "text-green-600" : "text-red-600"}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{r.description}</p>
                    <p className="text-xs text-gray-500">{r.category} · Próximo: {formatDate(r.next_due)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge className={`text-xs font-normal ${FREQUENCY_COLORS[r.frequency] ?? "bg-gray-100 text-gray-700"}`} variant="secondary">
                    {FREQUENCY_LABELS[r.frequency] ?? r.frequency}
                  </Badge>
                  <span className={`text-sm font-semibold ${r.type === "income" ? "text-green-600" : "text-red-600"}`}>
                    {r.type === "expense" ? "- " : "+ "}
                    {formatCurrency(r.amount)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Annual breakdown chart */}
      <div className="rounded-lg border bg-white p-4">
        <h2 className="mb-4 text-base font-semibold">Projeção anual por mês</h2>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            <Legend />
            <Bar dataKey="Receitas" fill="#22c55e" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Despesas" fill="#ef4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
