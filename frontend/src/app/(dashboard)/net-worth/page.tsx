"use client";

import { usePatrimonySnapshot, usePatrimonyHistory } from "@/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency } from "@/lib/format";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from "recharts";
import { TrendingUp, TrendingDown } from "lucide-react";

export default function NetWorthPage() {
    const { data: snapshot, isLoading: snapshotLoading } = usePatrimonySnapshot();
    const { data: history, isLoading: historyLoading } = usePatrimonyHistory(12);

    const isIncreasing = (history?.[history.length - 1]?.net_worth ?? 0) >= (history?.[0]?.net_worth ?? 0);

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Patrimônio</h1>
                <p className="text-muted-foreground text-sm mt-1">
                    Acompanhe a evolução do seu patrimônio líquido
                </p>
            </div>

            {/* Summary Cards */}
            {snapshotLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-[120px]" />
                    ))}
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">
                                Ativos
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold text-green-600">
                                {formatCurrency(snapshot?.total_assets ?? 0)}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                Caixa, fundos, renda fixa
                            </p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">
                                Passivos
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold text-red-600">
                                {formatCurrency(snapshot?.total_liabilities ?? 0)}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                Dívidas e empréstimos
                            </p>
                        </CardContent>
                    </Card>
                    <Card className="border-primary">
                        <CardHeader className="pb-2">
                            <CardTitle className="flex items-center justify-between">
                                <span className="text-sm text-muted-foreground">Patrimônio Líquido</span>
                                {isIncreasing ? (
                                    <TrendingUp className="h-4 w-4 text-green-600" />
                                ) : (
                                    <TrendingDown className="h-4 w-4 text-red-600" />
                                )}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold">{formatCurrency(snapshot?.net_worth ?? 0)}</p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Chart */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Evolução Histórica</CardTitle>
                </CardHeader>
                <CardContent>
                    {historyLoading ? (
                        <Skeleton className="h-[300px] w-full" />
                    ) : (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={history ?? []}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="date"
                                    tick={{ fontSize: 12 }}
                                />
                                <YAxis />
                                <RechartsTooltip
                                    formatter={(value) => formatCurrency(Number(value))}
                                    contentStyle={{
                                        borderRadius: "8px",
                                        border: "1px solid #e5e7eb",
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="net_worth"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    dot={{ fill: "#3b82f6", r: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    )}
                </CardContent>
            </Card>

            {/* Assets & Liabilities Details */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Ativos Detalhados</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {snapshotLoading ? (
                            <Skeleton className="h-[200px]" />
                        ) : (
                            <div className="space-y-3">
                                {(snapshot?.assets ?? []).map((asset, idx) => (
                                    <div key={idx} className="flex justify-between items-center pb-2 border-b last:border-b-0">
                                        <div>
                                            <p className="font-medium text-sm">{asset.name}</p>
                                            <p className="text-xs text-muted-foreground capitalize">{asset.type}</p>
                                        </div>
                                        <p className="font-semibold text-green-600">
                                            {formatCurrency(asset.value)}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Passivos Detalhados</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {snapshotLoading ? (
                            <Skeleton className="h-[200px]" />
                        ) : (
                            <div className="space-y-3">
                                {(snapshot?.liabilities ?? []).map((liability, idx) => (
                                    <div key={idx} className="flex justify-between items-center pb-2 border-b last:border-b-0">
                                        <div>
                                            <p className="font-medium text-sm">{liability.name}</p>
                                            <p className="text-xs text-muted-foreground capitalize">
                                                {liability.type}
                                            </p>
                                        </div>
                                        <p className="font-semibold text-red-600">
                                            {formatCurrency(liability.value)}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
