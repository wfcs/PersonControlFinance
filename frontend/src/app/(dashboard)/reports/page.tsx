"use client";

import { useDashboardSummary } from "@/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency, formatDate } from "@/lib/format";
import { PieChart, Pie, Cell, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

const COLORS = ["#0ea5e9", "#06b6d4", "#14b8a6", "#10b981", "#8b5cf6", "#f59e0b"];

export default function ReportsPage() {
    const { data: summary, isLoading } = useDashboardSummary();

    const handlePrint = () => {
        window.print();
    };

    const handleDownload = () => {
        const element = document.getElementById("report-content");
        if (!element) return;
        
        const link = document.createElement("a");
        link.href = URL.createObjectURL(new Blob([element.innerHTML], { type: "text/html" }));
        link.download = `relatorio-${formatDate(new Date())}.html`;
        link.click();
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Relatórios</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Visualize análises detalhadas de suas finanças
                    </p>
                </div>

                <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handlePrint}>
                        Imprimir
                    </Button>
                    <Button size="sm" onClick={handleDownload}>
                        <Download className="h-4 w-4 mr-1.5" />
                        Download
                    </Button>
                </div>
            </div>

            <div id="report-content" className="space-y-6">
                {/* Summary */}
                {isLoading ? (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <Skeleton key={i} className="h-[100px]" />
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 print:break-before-avoid">
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm text-muted-foreground">
                                    Receita
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-2xl font-bold text-green-600">
                                    {formatCurrency(summary?.summary?.income ?? 0)}
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm text-muted-foreground">
                                    Despesa
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-2xl font-bold text-red-600">
                                    {formatCurrency(summary?.summary?.expense ?? 0)}
                                </p>
                            </CardContent>
                        </Card>
                        <Card className="border-primary">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm text-primary">
                                    Resultado
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-2xl font-bold">
                                    {formatCurrency(summary?.summary?.balance ?? 0)}
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 print:break-before-avoid">
                    {/* Pie Chart */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Gastos por Categoria</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {isLoading ? (
                                <Skeleton className="h-[300px]" />
                            ) : (
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie
                                            data={
                                                (summary?.spending_by_category ?? [])
                                                    .filter((c) => c.total !== 0)
                                                    .slice(0, 6)
                                                    .map((c) => ({
                                                        name: c.category_name ?? "Sem categoria",
                                                        value: Math.abs(Number(c.total)),
                                                    })) ?? []
                                            }
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                                            outerRadius={100}
                                            fill="#8884d8"
                                            dataKey="value"
                                        >
                                            {(summary?.spending_by_category ?? []).map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            )}
                        </CardContent>
                    </Card>

                    {/* Category List */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Top Categorias</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {isLoading ? (
                                <Skeleton className="h-[300px]" />
                            ) : (
                                <div className="space-y-2">
                                    {(summary?.spending_by_category ?? [])
                                        .filter((c) => c.total !== 0)
                                        .slice(0, 8)
                                        .map((cat, idx) => (
                                            <div key={idx} className="flex justify-between items-center pb-2 border-b last:border-0">
                                                <p className="text-sm font-medium">
                                                    {cat.category_name ?? "Sem categoria"}
                                                </p>
                                                <p className="text-sm font-semibold">
                                                    {formatCurrency(Math.abs(Number(cat.total)))}
                                                </p>
                                            </div>
                                        ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
