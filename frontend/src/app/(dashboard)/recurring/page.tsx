"use client";

import { useRecurrences, useDetectRecurrences } from "@/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Zap, Plus } from "lucide-react";
import { useState } from "react";
import { formatCurrency, formatDate } from "@/lib/format";

export default function RecurringPage() {
    const { data: recurrences, isLoading } = useRecurrences();
    const detectRecurrences = useDetectRecurrences();
    const [accountId] = useState<string>("");

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Recorrentes</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Acompanhe despesas fixas e parcelas
                    </p>
                </div>

                <Button onClick={() => accountId && detectRecurrences.mutate(accountId)}>
                    <Zap className="h-4 w-4 mr-1.5" />
                    Detectar automaticamente
                </Button>
            </div>

            {/* Grid */}
            {isLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <Skeleton key={i} className="h-[180px]" />
                    ))}
                </div>
            ) : (recurrences ?? []).length === 0 ? (
                <Card>
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <Zap className="h-10 w-10 text-muted-foreground mb-3" />
                        <p className="text-muted-foreground">Nenhuma recorrência cadastrada</p>
                        <Button size="sm" className="mt-3">
                            <Plus className="h-4 w-4 mr-1.5" />
                            Nova recorrência
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {recurrences!.map((rec) => (
                        <Card key={rec.id}>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-base flex items-center justify-between">
                                    {rec.name}
                                    {rec.is_auto_detected && (
                                        <Badge variant="secondary" className="text-xs">
                                            Auto-detectada
                                        </Badge>
                                    )}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                <div>
                                    <p className="text-sm text-muted-foreground">Valor</p>
                                    <p className="text-xl font-bold">{formatCurrency(rec.amount)}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Frequência</p>
                                    <p className="text-sm font-medium capitalize">{rec.frequency}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Próxima ocorrência</p>
                                    <p className="text-sm">{formatDate(rec.next_occurrence)}</p>
                                </div>
                                {rec.confidence_score && (
                                    <div>
                                        <p className="text-sm text-muted-foreground">Confiança</p>
                                        <p className="text-sm font-medium">{(rec.confidence_score * 100).toFixed(0)}%</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
