"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Target } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { formatCurrency } from "@/lib/format";

const goalSchema = z.object({
    name: z.string().min(1, "Nome obrigatório"),
    target_amount: z.coerce.number().min(0.01, "Insira um valor"),
    target_date: z.string().min(1, "Data obrigatória"),
    description: z.string().optional(),
});

type GoalForm = z.infer<typeof goalSchema>;

export default function GoalsPage() {
    const [dialogOpen, setDialogOpen] = useState(false);

    // Simulando alguns dados de metas (em produção, viria de hooks)
    const sampleGoals = [
        {
            id: "1",
            name: "Emergência (3 meses)",
            target_amount: 15000,
            current_amount: 8500,
            target_date: "2026-06-30",
        },
        {
            id: "2",
            name: "Viagem para Dubai",
            target_amount: 25000,
            current_amount: 5000,
            target_date: "2026-12-31",
        },
        {
            id: "3",
            name: "Carro novo",
            target_amount: 80000,
            current_amount: 32000,
            target_date: "2027-12-31",
        },
    ];

    const {
        register,
        handleSubmit,
        reset,
        formState: { isSubmitting },
    } = useForm<GoalForm>({ resolver: zodResolver(goalSchema) as any });

    const onSubmit = async (values: GoalForm) => {
        // Implementação quando hooks estiverem prontos
        reset();
        setDialogOpen(false);
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Metas Financeiras</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Defina e acompanhe seus objetivos financeiros
                    </p>
                </div>

                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    {/* @ts-expect-error asChild Radix */}
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="h-4 w-4 mr-1.5" />
                            Nova meta
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Nova Meta Financeira</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-2">
                            <div className="space-y-2">
                                <Label>Nome da meta</Label>
                                <Input placeholder="Ex: Fundo de emergência" {...register("name")} />
                            </div>
                            <div className="space-y-2">
                                <Label>Valor alvo (R$)</Label>
                                <Input type="number" step="0.01" placeholder="0,00" {...register("target_amount")} />
                            </div>
                            <div className="space-y-2">
                                <Label>Data alvo</Label>
                                <Input type="date" {...register("target_date")} />
                            </div>
                            <div className="space-y-2">
                                <Label>Descrição (opcional)</Label>
                                <Input placeholder="Notas sobre a meta" {...register("description")} />
                            </div>
                            <Button type="submit" className="w-full" disabled={isSubmitting}>
                                Criar meta
                            </Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Goals Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {sampleGoals.map((goal) => {
                    const progress = (goal.current_amount / goal.target_amount) * 100;
                    const remaining = goal.target_amount - goal.current_amount;

                    return (
                        <Card key={goal.id} className="hover:shadow-md transition-shadow">
                            <CardHeader className="pb-3">
                                <CardTitle className="text-base flex items-center gap-2">
                                    <Target className="h-4 w-4" />
                                    {goal.name}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {/* Progress Bar */}
                                <div>
                                    <div className="flex justify-between mb-1">
                                        <p className="text-sm text-muted-foreground">Progresso</p>
                                        <p className="text-sm font-medium">{Math.round(progress)}%</p>
                                    </div>
                                    <div className="w-full bg-secondary rounded-full h-2">
                                        <div
                                            className="bg-primary h-2 rounded-full transition-all"
                                            style={{ width: `${Math.min(progress, 100)}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Amount Info */}
                                <div className="space-y-2 pt-2 border-t">
                                    <div className="flex justify-between">
                                        <p className="text-sm text-muted-foreground">Alcançado</p>
                                        <p className="font-medium">{formatCurrency(goal.current_amount)}</p>
                                    </div>
                                    <div className="flex justify-between">
                                        <p className="text-sm text-muted-foreground">Alvo</p>
                                        <p className="font-medium">{formatCurrency(goal.target_amount)}</p>
                                    </div>
                                    <div className="flex justify-between">
                                        <p className="text-sm text-muted-foreground">Falta</p>
                                        <p className="font-medium text-amber-600">{formatCurrency(remaining)}</p>
                                    </div>
                                </div>

                                {/* Target Date */}
                                <div className="bg-muted p-2 rounded text-xs text-center text-muted-foreground">
                                    Prazo: {new Date(goal.target_date).toLocaleDateString("pt-BR")}
                                </div>

                                {/* Action Buttons */}
                                <div className="flex gap-2 pt-2">
                                    <Button size="sm" className="flex-1">
                                        Contribuir
                                    </Button>
                                    <Button size="sm" variant="outline" className="flex-1">
                                        Editar
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}
