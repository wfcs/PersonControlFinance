"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  useDashboardSummary,
  useSpendingByCategory,
  useTransactions,
} from "@/hooks";
import { formatCurrency, formatDate } from "@/lib/format";

// Mock spending-over-time data for the line chart
const SPENDING_TREND = [
  { month: "Out", receitas: 5200, despesas: 3100 },
  { month: "Nov", receitas: 5400, despesas: 3400 },
  { month: "Dez", receitas: 6200, despesas: 4200 },
  { month: "Jan", receitas: 5600, despesas: 3000 },
  { month: "Fev", receitas: 5700, despesas: 3150 },
  { month: "Mar", receitas: 5800, despesas: 3260 },
];

function SummaryCardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-2">
        <Skeleton className="h-4 w-28" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-7 w-36 mb-1" />
        <Skeleton className="h-3 w-20" />
      </CardContent>
    </Card>
  );
}

function TransactionRowSkeleton() {
  return (
    <div className="flex items-center justify-between py-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-8 w-8 rounded-full" />
        <div>
          <Skeleton className="h-4 w-32 mb-1" />
          <Skeleton className="h-3 w-20" />
        </div>
      </div>
      <Skeleton className="h-4 w-20" />
    </div>
  );
}

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useDashboardSummary();
  const { data: spending, isLoading: spendingLoading } = useSpendingByCategory();
  const { data: transactions, isLoading: transactionsLoading } = useTransactions({
    limit: 5,
  });

  const resultado = (summary?.totalIncome ?? 0) - (summary?.totalExpenses ?? 0);
  const resultadoPositivo = resultado >= 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {summaryLoading ? (
          <>
            <SummaryCardSkeleton />
            <SummaryCardSkeleton />
            <SummaryCardSkeleton />
            <SummaryCardSkeleton />
          </>
        ) : (
          <>
            {/* Saldo Total */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Saldo Total
                </CardTitle>
                <Wallet className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatCurrency(summary?.totalBalance ?? 0)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Todas as contas
                </p>
              </CardContent>
            </Card>

            {/* Receitas */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Receitas
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-emerald-500" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-emerald-600">
                  {formatCurrency(summary?.totalIncome ?? 0)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Este mês</p>
              </CardContent>
            </Card>

            {/* Despesas */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Despesas
                </CardTitle>
                <TrendingDown className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-red-600">
                  {formatCurrency(summary?.totalExpenses ?? 0)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Este mês</p>
              </CardContent>
            </Card>

            {/* Resultado */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Resultado
                </CardTitle>
                {resultadoPositivo ? (
                  <ArrowUpRight className="h-4 w-4 text-emerald-500" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-red-500" />
                )}
              </CardHeader>
              <CardContent>
                <p
                  className={`text-2xl font-bold ${
                    resultadoPositivo ? "text-emerald-600" : "text-red-600"
                  }`}
                >
                  {formatCurrency(resultado)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Taxa de poupança: {summary?.savingsRate?.toFixed(1)}%
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Line Chart - Ritmo de gastos */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Ritmo de gastos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={SPENDING_TREND}>
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 12, fill: "#6b7280" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: "#6b7280" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) =>
                    new Intl.NumberFormat("pt-BR", {
                      notation: "compact",
                      style: "currency",
                      currency: "BRL",
                    }).format(v)
                  }
                />
                <Tooltip
                  formatter={(value, name) => [
                    formatCurrency(Number(value)),
                    String(name) === "receitas" ? "Receitas" : "Despesas",
                  ]}
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid #e5e7eb",
                    fontSize: "12px",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="receitas"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="despesas"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-2 justify-center">
              <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="w-3 h-0.5 bg-emerald-500 inline-block rounded" />
                Receitas
              </span>
              <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="w-3 h-0.5 bg-red-500 inline-block rounded" />
                Despesas
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Pie Chart - Gastos por categoria */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Gastos por categoria
            </CardTitle>
          </CardHeader>
          <CardContent>
            {spendingLoading ? (
              <div className="flex flex-col items-center gap-3">
                <Skeleton className="h-40 w-40 rounded-full" />
                <div className="space-y-2 w-full">
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-3/4" />
                </div>
              </div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={160}>
                  <PieChart>
                    <Pie
                      data={spending}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      dataKey="amount"
                      nameKey="category"
                    >
                      {spending?.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value) => [
                        formatCurrency(Number(value)),
                        "Valor",
                      ]}
                      contentStyle={{
                        borderRadius: "8px",
                        border: "1px solid #e5e7eb",
                        fontSize: "12px",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <ul className="space-y-1.5 mt-2">
                  {spending?.map((item, index) => (
                    <li
                      key={index}
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="flex items-center gap-1.5 text-muted-foreground">
                        <span
                          className="w-2 h-2 rounded-full shrink-0"
                          style={{ backgroundColor: item.color }}
                        />
                        {item.category}
                      </span>
                      <span className="font-medium">
                        {item.percentage.toFixed(0)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Transações recentes
          </CardTitle>
        </CardHeader>
        <CardContent>
          {transactionsLoading ? (
            <div className="divide-y">
              {Array.from({ length: 5 }).map((_, i) => (
                <TransactionRowSkeleton key={i} />
              ))}
            </div>
          ) : !transactions || transactions.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              Nenhuma transação encontrada.
            </p>
          ) : (
            <div className="divide-y">
              {transactions.slice(0, 5).map((tx) => {
                const isIncome = tx.type === "income";
                const isTransfer = tx.type === "transfer";
                return (
                  <div
                    key={tx.id}
                    className="flex items-center justify-between py-3"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${
                          isIncome
                            ? "bg-emerald-100"
                            : isTransfer
                            ? "bg-blue-100"
                            : "bg-red-100"
                        }`}
                      >
                        {isIncome ? (
                          <ArrowUpRight className="h-4 w-4 text-emerald-600" />
                        ) : isTransfer ? (
                          <ArrowUpRight className="h-4 w-4 text-blue-600" />
                        ) : (
                          <ArrowDownRight className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900 leading-none">
                          {tx.description}
                        </p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {formatDate(tx.date)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-sm font-semibold ${
                          isIncome
                            ? "text-emerald-600"
                            : isTransfer
                            ? "text-blue-600"
                            : "text-red-600"
                        }`}
                      >
                        {isIncome ? "+" : isTransfer ? "" : "-"}
                        {formatCurrency(tx.amount)}
                      </span>
                      <Badge
                        variant="secondary"
                        className="text-xs hidden sm:inline-flex"
                      >
                        {isIncome
                          ? "Receita"
                          : isTransfer
                          ? "Transferência"
                          : "Despesa"}
                      </Badge>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
