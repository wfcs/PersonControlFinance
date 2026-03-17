"use client";

import { useBalanceProjection } from "@/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency } from "@/lib/format";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Alert, AlertTriangle } from "recharts";
import { useState } from "react";

export default function ProjectionPage() {
    const [months, setMonths] = useState(6);
    const { data: projection, isLoading } = useBalanceProjection(months);

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Projeção de Saldo</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Visualize saldo estimado para os próximos meses
                    </p>
                </div>

                <div className="flex gap-2">
                    {[3, 6, 12].map((m) => (
                        <Badge
                            key={m}
                            variant={months === m ? "default" : "secondary"}
                            className="cursor-pointer"
                            onClick={() => setMonths(m)}
                        >
                            {m}M
                        </Badge>
                    ))}
                </div>
            </div>

            {/* Current Balance */}
            {isLoading ? (
                <Skeleton className="h-[100px]" />
            ) : (
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-muted-foreground">
                            Saldo Atual
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold">{formatCurrency(projection?.current_balance ?? 0)}</p>
                    </CardContent>
                </Card>
            )}

            {/* Warnings */}
            {(projection?.warnings ?? []).length > 0 && (
                <div className="space-y-2">
                    {projection!.warnings.map((warning, idx) => (
                        <div
                            key={idx}
                            className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                        >
                            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="text-sm font-medium text-yellow-900">{warning.month}</p>
                                <p className="text-sm text-yellow-700">{warning.message}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Chart */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Projeção Mensal</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <Skeleton className="h-[300px] w-full" />
                    ) : (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={projection?.projections ?? []}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="month" />
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
                                    dataKey="projected_balance"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    dot={{ fill: "#3b82f6", r: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    )}
                </CardContent>
            </Card>

            {/* Detail Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Detalhamento</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <Skeleton className="h-[200px] w-full" />
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b">
                                        <th className="text-left py-2 font-medium">Mês</th>
                                        <th className="text-right py-2 font-medium">Receitas</th>
                                        <th className="text-right py-2 font-medium">Gastos</th>
                                        <th className="text-right py-2 font-medium">Saldo Projetado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(projection?.projections ?? []).map((p, idx) => (
                                        <tr key={idx} className="border-b hover:bg-muted/50">
                                            <td className="py-2">{p.month}</td>
                                            <td className="text-right text-green-600">
                                                {formatCurrency(p.income)}
                                            </td>
                                            <td className="text-right text-red-600">
                                                {formatCurrency(p.expenses)}
                                            </td>
                                            <td className="text-right font-medium">
                                                {formatCurrency(p.projected_balance)}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
