"use client";

import { useBills, useBillSummary, useMarkBillAsPaid } from "@/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency, formatDate } from "@/lib/format";
import { useState } from "react";

export default function InvoicesPage() {
    const [month, setMonth] = useState(new Date().getMonth() + 1);
    const [year, setYear] = useState(new Date().getFullYear());

    const { data: summary, isLoading } = useBillSummary(month, year);
    const { data: bills } = useBills(month, year);
    const markAsPaid = useMarkBillAsPaid();

    const statusColors: Record<string, string> = {
        open: "bg-yellow-50 text-yellow-600 border-yellow-200",
        partial: "bg-blue-50 text-blue-600 border-blue-200",
        closed: "bg-green-50 text-green-600 border-green-200",
        overdue: "bg-red-50 text-red-600 border-red-200",
    };

    const statusLabels: Record<string, string> = {
        open: "Em aberto",
        partial: "Parcialmente pago",
        closed: "Fechado",
        overdue: "Vencido",
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Faturas</h1>
                <p className="text-muted-foreground text-sm mt-1">
                    Acompanhe seus pagamentos de cartão de crédito
                </p>
            </div>

            {/* Summary */}
            {isLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                    {Array.from({ length: 4 }).map((_, i) => (
                        <Skeleton key={i} className="h-[100px]" />
                    ))}
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">
                                Despesas Fixas
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold">{formatCurrency(summary?.total_fixed ?? 0)}</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">
                                Parcelas
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold">
                                {formatCurrency(summary?.total_installments ?? 0)}
                            </p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">
                                Avulsas
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold">{formatCurrency(summary?.total_avulsas ?? 0)}</p>
                        </CardContent>
                    </Card>
                    <Card className="border-primary">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-primary">
                                Total do Mês
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold">{formatCurrency(summary?.grand_total ?? 0)}</p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Bills List */}
            <div className="space-y-4">
                <h2 className="text-xl font-semibold">Cartões</h2>
                {isLoading ? (
                    <div className="space-y-4">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <Skeleton key={i} className="h-[150px]" />
                        ))}
                    </div>
                ) : (bills ?? []).length === 0 ? (
                    <Card>
                        <CardContent className="flex items-center justify-center py-12">
                            <p className="text-muted-foreground">Nenhuma fatura neste período</p>
                        </CardContent>
                    </Card>
                ) : (
                    bills!.map((bill) => (
                        <Card key={bill.id}>
                            <CardHeader className="pb-3">
                                <div className="flex items-center justify-between">
                                    <CardTitle className="text-base">
                                        {bill.account_id}
                                    </CardTitle>
                                    <Badge
                                        className={`text-xs ${statusColors[bill.status] ?? statusColors.open}`}
                                    >
                                        {statusLabels[bill.status] ?? bill.status}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <p className="text-sm text-muted-foreground">Vencimento</p>
                                        <p className="font-medium">{formatDate(bill.due_date)}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Total</p>
                                        <p className="font-medium">{formatCurrency(bill.total_amount)}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Pago</p>
                                        <p className="font-medium">{formatCurrency(bill.total_paid)}</p>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => markAsPaid.mutate(bill.id)}
                                    >
                                        Marcar como pago
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
}
