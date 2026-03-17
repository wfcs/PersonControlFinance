"use client";

import { useCashFlow } from "@/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell } from "recharts";
import { formatCurrency } from "@/lib/format";

const COLORS = ["#16a34a", "#dc2626"];

export default function CashFlowPage() {
    const { data: cashFlow, isLoading } = useCashFlow(12);

    const data = (cashFlow ?? []).map((p) => ({
        name: `${p.month}/${p.year}`,
        Receita: Number(p.income),
        Gasto: Number(p.expense),
        Saldo: Number(p.balance),
    }));

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Fluxo de Caixa</h1>
                <p className="text-muted-foreground text-sm mt-1">
                    Visualize receitas e despesas ao longo do tempo
                </p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {isLoading ? (
                    <>
                        <Skeleton className="h-[100px]" />
                        <Skeleton className="h-[100px]" />
                        <Skeleton className="h-[100px]" />
                    </>
                ) : (
                    <>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm text-muted-foreground">
                                    Receita Total
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-2xl font-bold">
                                    {formatCurrency(
                                        (cashFlow ?? []).reduce((sum, p) => sum + Number(p.income), 0)
                                    )}
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm text-muted-foreground">
                                    Gasto Total
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-2xl font-bold text-destructive">
                                    {formatCurrency(
                                        Math.abs((cashFlow ?? []).reduce((sum, p) => sum + Number(p.expense), 0))
                                    )}
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm text-muted-foreground">
                                    Saldo Total
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-2xl font-bold">
                                    {formatCurrency((cashFlow ?? []).reduce((sum, p) => sum + Number(p.balance), 0))}
                                </p>
                            </CardContent>
                        </Card>
                    </>
                )}
            </div>

            {/* Chart */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Composição mensal</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <Skeleton className="h-[300px] w-full" />
                    ) : (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <RechartsTooltip
                                    formatter={(value) => formatCurrency(Number(value))}
                                    contentStyle={{
                                        borderRadius: "8px",
                                        border: "1px solid #e5e7eb",
                                    }}
                                />
                                <Bar dataKey="Receita" fill={COLORS[0]} />
                                <Bar dataKey="Gasto" fill={COLORS[1]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
