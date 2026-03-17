"use client";

import { useDashboardSummary, useCashFlow } from "@/hooks/use-dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency, formatDate } from "@/lib/format";
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    ArrowUpRight,
    ArrowDownRight,
} from "lucide-react";
import {
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    Cell,
} from "recharts";

const CHART_COLORS = [
    "oklch(0.60 0.17 160)",
    "oklch(0.55 0.18 250)",
    "oklch(0.65 0.16 45)",
    "oklch(0.55 0.20 310)",
    "oklch(0.58 0.24 27)",
    "oklch(0.70 0.12 200)",
];

const MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

export default function DashboardPage() {
    const { data: summary, isLoading: summaryLoading } = useDashboardSummary();
    const { data: cashFlow, isLoading: cashFlowLoading } = useCashFlow(6);

    const income = summary?.summary?.income ?? 0;
    const expense = summary?.summary?.expense ?? 0;
    const balance = summary?.summary?.balance ?? 0;

    const cashFlowData = (cashFlow ?? []).map((p) => ({
        name: MONTHS[p.month - 1],
        Receita: Number(p.income),
        Gasto: Math.abs(Number(p.expense)),
    }));

    const categoryData = (summary?.spending_by_category ?? [])
        .filter((c) => c.total !== 0)
        .slice(0, 6)
        .map((c) => ({
            name: c.category_name ?? "Sem categoria",
            value: Math.abs(Number(c.total)),
        }));

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 animate-fade-in-scale">
                <SummaryCard
                    title="Receita"
                    value={income}
                    icon={<TrendingUp className="h-5 w-5" />}
                    trend="income"
                    loading={summaryLoading}
                />
                <SummaryCard
                    title="Gastos"
                    value={expense}
                    icon={<TrendingDown className="h-5 w-5" />}
                    trend="expense"
                    loading={summaryLoading}
                />
                <SummaryCard
                    title="Resultado"
                    value={balance}
                    icon={<DollarSign className="h-5 w-5" />}
                    trend={balance >= 0 ? "income" : "expense"}
                    loading={summaryLoading}
                />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 animate-slide-in-bottom">
                {/* Cash Flow Chart */}
                <Card className="lg:col-span-2 card-modern">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-semibold uppercase tracking-wide text-muted-foreground flex items-center gap-2">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                            Fluxo de Caixa
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {cashFlowLoading ? (
                            <Skeleton className="h-[240px] w-full" />
                        ) : (
                            <ResponsiveContainer width="100%" height={240}>
                                <AreaChart data={cashFlowData}>
                                    <defs>
                                        <linearGradient id="gradIncome" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="oklch(0.60 0.17 160)" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="oklch(0.60 0.17 160)" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="gradExpense" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="oklch(0.58 0.24 27)" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="oklch(0.58 0.24 27)" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.90 0 0)" />
                                    <XAxis
                                        dataKey="name"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fontSize: 12, fill: "oklch(0.52 0.02 260)" }}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fontSize: 12, fill: "oklch(0.52 0.02 260)" }}
                                        tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                                    />
                                    <RechartsTooltip
                                        formatter={(value) => formatCurrency(Number(value))}
                                        contentStyle={{
                                            borderRadius: "8px",
                                            border: "1px solid oklch(0.92 0.005 260)",
                                            boxShadow: "0 4px 12px oklch(0 0 0 / 8%)",
                                        }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="Receita"
                                        stroke="oklch(0.60 0.17 160)"
                                        fill="url(#gradIncome)"
                                        strokeWidth={2}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="Gasto"
                                        stroke="oklch(0.58 0.24 27)"
                                        fill="url(#gradExpense)"
                                        strokeWidth={2}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        )}
                    </CardContent>
                </Card>

                {/* Category Spending */}
                <Card className="card-modern">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-semibold uppercase tracking-wide text-muted-foreground flex items-center gap-2">
                            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                            Gastos por Categoria
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {summaryLoading ? (
                            <div className="space-y-3">
                                {Array.from({ length: 5 }).map((_, i) => (
                                    <Skeleton key={i} className="h-6 w-full" />
                                ))}
                            </div>
                        ) : categoryData.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-8">
                                Sem dados no período
                            </p>
                        ) : (
                            <ResponsiveContainer width="100%" height={240}>
                                <BarChart data={categoryData} layout="vertical" barCategoryGap={8}>
                                    <XAxis type="number" hide />
                                    <YAxis
                                        type="category"
                                        dataKey="name"
                                        width={100}
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fontSize: 11, fill: "oklch(0.52 0.02 260)" }}
                                    />
                                    <RechartsTooltip
                                        formatter={(value) => formatCurrency(Number(value))}
                                        contentStyle={{
                                            borderRadius: "8px",
                                            border: "1px solid oklch(0.92 0.005 260)",
                                        }}
                                    />
                                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                        {categoryData.map((_, i) => (
                                            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Recent Transactions */}
            <Card className="card-modern animate-slide-in-top">
                <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold uppercase tracking-wide text-muted-foreground flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                        Transações Recentes
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {summaryLoading ? (
                        <div className="space-y-3">
                            {Array.from({ length: 5 }).map((_, i) => (
                                <Skeleton key={i} className="h-12 w-full" />
                            ))}
                        </div>
                    ) : (summary?.recent_transactions ?? []).length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-8">
                            Nenhuma transação registrada ainda
                        </p>
                    ) : (
                        <div className="divide-y">
                            {(summary?.recent_transactions ?? []).slice(0, 8).map((tx: Record<string, unknown>, i) => {
                                const amount = Number(tx.amount ?? 0);
                                const isIncome = amount >= 0;
                                return (
                                    <div
                                        key={String(tx.id ?? i)}
                                        className="flex items-center justify-between py-3 first:pt-0 last:pb-0"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div
                                                className={`w-8 h-8 rounded-lg flex items-center justify-center ${isIncome
                                                    ? "bg-emerald-50 text-emerald-600"
                                                    : "bg-destructive/10 text-destructive"
                                                    }`}
                                            >
                                                {isIncome ? (
                                                    <ArrowUpRight className="h-4 w-4" />
                                                ) : (
                                                    <ArrowDownRight className="h-4 w-4" />
                                                )}
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium">{String(tx.description ?? "—")}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {tx.date ? formatDate(String(tx.date)) : ""}
                                                </p>
                                            </div>
                                        </div>
                                        <span
                                            className={`text-sm font-semibold tabular-nums ${isIncome ? "text-emerald-600" : "text-destructive"
                                                }`}
                                        >
                                            {isIncome ? "+" : ""}
                                            {formatCurrency(amount)}
                                        </span>
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

/* ── Summary Card component ──────────────────────────────────────── */
function SummaryCard({
    title,
    value,
    icon,
    trend,
    loading,
}: {
    title: string;
    value: number;
    icon: React.ReactNode;
    trend: "income" | "expense";
    loading: boolean;
}) {
    return (
        <Card className="card-modern relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-transparent group-hover:from-blue-500/5 transition-all duration-500" />
            <CardContent className="pt-5 relative z-10">
                <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        {title}
                    </span>
                    <div
                        className={`p-2 rounded-lg transition-all duration-300 ${
                            trend === "income"
                                ? "bg-gradient-to-br from-emerald-50 to-emerald-100 text-emerald-600 group-hover:shadow-lg group-hover:shadow-emerald-200"
                                : "bg-gradient-to-br from-destructive/10 to-destructive/20 text-destructive group-hover:shadow-lg group-hover:shadow-destructive/20"
                        }`}
                    >
                        {icon}
                    </div>
                </div>
                {loading ? (
                    <Skeleton className="h-8 w-40 rounded-lg" />
                ) : (
                    <div className="space-y-1">
                        <p className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                            {formatCurrency(Math.abs(value))}
                        </p>
                        <p className="text-xs text-muted-foreground">
                            {trend === "income" ? "✓ Receitas do mês" : "→ Despesas do período"}
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
