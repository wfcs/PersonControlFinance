"use client";

import { useCategories, useCategoryWithStats, useCreateCategory, useUpdateCategory, useDeleteCategory } from "@/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Edit, Trash2, TrendingUp } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { formatCurrency } from "@/lib/format";

const categorySchema = z.object({
    name: z.string().min(1, "Nome obrigatório"),
    monthly_limit: z.coerce.number().optional(),
    color: z.string().optional(),
    icon: z.string().optional(),
});

type CategoryForm = z.infer<typeof categorySchema>;

export default function CategoriesPage() {
    const { data: categories, isLoading } = useCategories();
    const createCategory = useCreateCategory();
    const updateCategory = useUpdateCategory();
    const deleteCategory = useDeleteCategory();
    const [dialogOpen, setDialogOpen] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        reset,
        formState: { isSubmitting },
    } = useForm<CategoryForm>({ resolver: zodResolver(categorySchema) as any });

    const onSubmit = async (values: CategoryForm) => {
        if (editingId) {
            await updateCategory.mutateAsync({ id: editingId, ...values });
            setEditingId(null);
        } else {
            await createCategory.mutateAsync(values);
        }
        reset();
        setDialogOpen(false);
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Categorias</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Organize e acompanhe seus gastos por categoria
                    </p>
                </div>

                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    {/* @ts-expect-error asChild Radix */}
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="h-4 w-4 mr-1.5" />
                            Nova categoria
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>
                                {editingId ? "Editar categoria" : "Nova categoria"}
                            </DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-2">
                            <div className="space-y-2">
                                <Label>Nome</Label>
                                <Input placeholder="Ex: Alimentação" {...register("name")} />
                            </div>
                            <div className="space-y-2">
                                <Label>Limite mensal (R$)</Label>
                                <Input type="number" step="0.01" placeholder="0,00" {...register("monthly_limit")} />
                            </div>
                            <Button type="submit" className="w-full" disabled={isSubmitting}>
                                {editingId ? "Atualizar" : "Criar"}
                            </Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Grid de categorias */}
            {isLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <Skeleton key={i} className="h-[200px]" />
                    ))}
                </div>
            ) : (categories ?? []).length === 0 ? (
                <Card>
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <TrendingUp className="h-10 w-10 text-muted-foreground mb-3" />
                        <p className="text-muted-foreground">Nenhuma categoria cadastrada</p>
                        <Button size="sm" className="mt-3" onClick={() => setDialogOpen(true)}>
                            <Plus className="h-4 w-4 mr-1.5" />
                            Criar primeira categoria
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {categories!.map((cat) => (
                        <CategoryCard
                            key={cat.id}
                            category={cat}
                            onEdit={() => {
                                setEditingId(cat.id);
                                setDialogOpen(true);
                            }}
                            onDelete={() => deleteCategory.mutate(cat.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

function CategoryCard({
    category,
    onEdit,
    onDelete,
}: {
    category: any;
    onEdit: () => void;
    onDelete: () => void;
}) {
    const { data: stats } = useCategoryWithStats(category.id);

    return (
        <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{category.name}</CardTitle>
                    <div className="flex gap-1">
                        <Button variant="ghost" size="sm" onClick={onEdit}>
                            <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={onDelete}>
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-3">
                {stats ? (
                    <>
                        <div>
                            <p className="text-sm text-muted-foreground">Gasto este mês</p>
                            <p className="text-xl font-bold">{formatCurrency(stats.current_month_spent)}</p>
                        </div>
                        {category.monthly_limit && (
                            <div>
                                <div className="flex justify-between mb-1">
                                    <p className="text-sm text-muted-foreground">Limite</p>
                                    <p className="text-sm font-medium">{stats.percentage_used}%</p>
                                </div>
                                <div className="w-full bg-secondary rounded-full h-2">
                                    <div
                                        className="bg-primary h-2 rounded-full transition-all"
                                        style={{ width: `${Math.min(stats.percentage_used, 100)}%` }}
                                    />
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {formatCurrency(category.monthly_limit)} de limite
                                </p>
                            </div>
                        )}
                    </>
                ) : (
                    <Skeleton className="h-20 w-full" />
                )}
            </CardContent>
        </Card>
    );
}
