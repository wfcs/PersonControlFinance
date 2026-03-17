"use client";

import { useState } from "react";
import {
    useTransactions,
    useCreateTransaction,
    useDeleteTransaction,
    type TransactionFilters,
    type TransactionCreate,
} from "@/hooks/use-transactions";
import { useAccounts } from "@/hooks/use-accounts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { formatCurrency, formatDate } from "@/lib/format";
import {
    Plus,
    Download,
    Search,
    ChevronLeft,
    ChevronRight,
    ArrowUpRight,
    ArrowDownRight,
    Trash2,
} from "lucide-react";
import { api } from "@/lib/api";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const txSchema = z.object({
    description: z.string().min(1, "Descrição obrigatória"),
    amount: z.preprocess((v) => Number(v), z.number().refine((n) => n !== 0, "Insira um valor")),
    type: z.enum(["debit", "credit", "pix", "transfer"]),
    date: z.string().min(1, "Data obrigatória"),
    account_id: z.string().min(1, "Selecione uma conta"),
    notes: z.string().optional(),
});

type TxForm = z.infer<typeof txSchema>;

export default function TransactionsPage() {
    const [filters, setFilters] = useState<TransactionFilters>({
        page: 1,
        page_size: 20,
    });
    const [search, setSearch] = useState("");
    const [typeFilter, setTypeFilter] = useState<string>("all");
    const [dialogOpen, setDialogOpen] = useState(false);

    const activeFilters: TransactionFilters = {
        ...filters,
        search: search || undefined,
        type: typeFilter === "all" ? undefined : typeFilter,
    };

    const { data, isLoading } = useTransactions(activeFilters);
    const { data: accounts } = useAccounts();
    const createTx = useCreateTransaction();
    const deleteTx = useDeleteTransaction();

    const {
        register,
        handleSubmit,
        reset,
        setValue,
        formState: { errors, isSubmitting },
    } = useForm<TxForm>({ resolver: zodResolver(txSchema) as any });

    const onSubmit = async (values: TxForm) => {
        const body: TransactionCreate = {
            ...values,
            amount: values.type === "debit" ? -Math.abs(values.amount) : Math.abs(values.amount),
            date: new Date(values.date).toISOString(),
        };
        await createTx.mutateAsync(body);
        reset();
        setDialogOpen(false);
    };

    const handleExportCSV = async () => {
        const params = new URLSearchParams();
        if (activeFilters.date_from) params.set("date_from", activeFilters.date_from);
        if (activeFilters.date_to) params.set("date_to", activeFilters.date_to);
        const response = await api.get(`/transactions/export/csv?${params}`, {
            responseType: "blob",
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const a = document.createElement("a");
        a.href = url;
        a.download = "transacoes.csv";
        a.click();
        window.URL.revokeObjectURL(url);
    };

    const totalPages = Math.ceil((data?.total ?? 0) / (filters.page_size ?? 20));

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="animate-fade-in-scale">
                <h1 className="text-3xl font-bold mb-1">Transações</h1>
                <p className="text-muted-foreground">Gerencie e acompanhe todas as suas transações financeiras</p>
            </div>

            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 bg-card/50 rounded-lg border border-border/50 backdrop-blur-sm hover:bg-card/70 transition-colors">
                <div className="flex items-center gap-2 flex-1 w-full sm:w-auto">
                    <div className="relative flex-1 max-w-sm">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Buscar transação..."
                            className="pl-9 h-10 rounded-lg border-border/50 focus:border-primary/50 focus:ring-1 focus:ring-primary/20"
                            value={search}
                            onChange={(e) => {
                                setSearch(e.target.value);
                                setFilters((f) => ({ ...f, page: 1 }));
                            }}
                        />
                    </div>
                    <Select
                        value={typeFilter}
                        onValueChange={(v) => {
                            setTypeFilter(v ?? "all");
                            setFilters((f) => ({ ...f, page: 1 }));
                        }}
                    >
                        <SelectTrigger className="w-[140px] h-10 rounded-lg border-border/50 focus:border-primary/50 focus:ring-1 focus:ring-primary/20">
                            <SelectValue placeholder="Tipo" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Todos</SelectItem>
                            <SelectItem value="debit">Débito</SelectItem>
                            <SelectItem value="credit">Crédito</SelectItem>
                            <SelectItem value="pix">Pix</SelectItem>
                            <SelectItem value="transfer">Transferência</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="flex items-center gap-2">
                    <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleExportCSV}
                        className="rounded-lg border-border/50 hover:bg-accent transition-colors"
                    >
                        <Download className="h-4 w-4 mr-1.5" />
                        CSV
                    </Button>
                    <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                        {/* @ts-expect-error asChild Radix compatibility */}
                        <DialogTrigger asChild>
                            <Button size="sm" className="bg-gradient-to-r from-primary to-primary/90 hover:shadow-lg hover:shadow-primary/20 transition-all rounded-lg">
                                <Plus className="h-4 w-4 mr-1.5" />
                                Nova transação
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[480px] rounded-xl">
                            <DialogHeader>
                                <DialogTitle className="text-xl font-bold">Nova Transação</DialogTitle>
                            </DialogHeader>
                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-4">
                                <div className="space-y-2">
                                    <Label htmlFor="description" className="text-sm font-semibold">Descrição</Label>
                                    <Input placeholder="Ex: Supermercado" {...register("description")} />
                                    {errors.description && (
                                        <p className="text-destructive text-xs">{errors.description.message}</p>
                                    )}
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-2">
                                        <Label>Valor (R$)</Label>
                                        <Input type="number" step="0.01" placeholder="0,00" {...register("amount")} />
                                        {errors.amount && (
                                            <p className="text-destructive text-xs">{errors.amount.message}</p>
                                        )}
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Tipo</Label>
                                        <Select onValueChange={(v) => setValue("type", v as TxForm["type"])}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Selecione" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="debit">Débito</SelectItem>
                                                <SelectItem value="credit">Crédito</SelectItem>
                                                <SelectItem value="pix">Pix</SelectItem>
                                                <SelectItem value="transfer">Transferência</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        {errors.type && (
                                            <p className="text-destructive text-xs">{errors.type.message}</p>
                                        )}
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-2">
                                        <Label>Data</Label>
                                        <Input type="date" {...register("date")} />
                                        {errors.date && (
                                            <p className="text-destructive text-xs">{errors.date.message}</p>
                                        )}
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Conta</Label>
                                        <Select onValueChange={(v) => setValue("account_id", String(v ?? ""))}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Selecione" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {(accounts ?? []).map((acc) => (
                                                    <SelectItem key={acc.id} value={acc.id}>
                                                        {acc.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        {errors.account_id && (
                                            <p className="text-destructive text-xs">{errors.account_id.message}</p>
                                        )}
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <Label>Observações</Label>
                                    <Input placeholder="Opcional" {...register("notes")} />
                                </div>
                                <Button type="submit" className="w-full" disabled={isSubmitting}>
                                    Salvar
                                </Button>
                            </form>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            {/* Table */}
            <Card>
                <CardContent className="p-0">
                    {isLoading ? (
                        <div className="p-4 space-y-3">
                            {Array.from({ length: 8 }).map((_, i) => (
                                <Skeleton key={i} className="h-12 w-full" />
                            ))}
                        </div>
                    ) : (data?.items ?? []).length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16 text-center">
                            <p className="text-muted-foreground text-sm">Nenhuma transação encontrada</p>
                            <Button
                                size="sm"
                                className="mt-3"
                                onClick={() => setDialogOpen(true)}
                            >
                                <Plus className="h-4 w-4 mr-1.5" />
                                Criar primeira transação
                            </Button>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-10"></TableHead>
                                    <TableHead>Descrição</TableHead>
                                    <TableHead className="hidden md:table-cell">Data</TableHead>
                                    <TableHead className="hidden md:table-cell">Tipo</TableHead>
                                    <TableHead className="text-right">Valor</TableHead>
                                    <TableHead className="w-10"></TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data!.items.map((tx) => {
                                    const isIncome = Number(tx.amount) >= 0;
                                    return (
                                        <TableRow key={tx.id}>
                                            <TableCell>
                                                <div
                                                    className={`w-7 h-7 rounded-md flex items-center justify-center ${isIncome
                                                        ? "bg-emerald-50 text-emerald-600"
                                                        : "bg-destructive/10 text-destructive"
                                                        }`}
                                                >
                                                    {isIncome ? (
                                                        <ArrowUpRight className="h-3.5 w-3.5" />
                                                    ) : (
                                                        <ArrowDownRight className="h-3.5 w-3.5" />
                                                    )}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <p className="font-medium text-sm">{tx.description}</p>
                                                {tx.installment_total && (
                                                    <span className="text-xs text-muted-foreground">
                                                        Parcela {tx.installment_number}/{tx.installment_total}
                                                    </span>
                                                )}
                                            </TableCell>
                                            <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                                                {formatDate(tx.date)}
                                            </TableCell>
                                            <TableCell className="hidden md:table-cell">
                                                <Badge variant="secondary" className="text-xs font-normal capitalize">
                                                    {tx.type}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <span
                                                    className={`text-sm font-semibold tabular-nums ${isIncome ? "text-emerald-600" : "text-destructive"
                                                        }`}
                                                >
                                                    {isIncome ? "+" : ""}
                                                    {formatCurrency(Number(tx.amount))}
                                                </span>
                                            </TableCell>
                                            <TableCell>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-7 w-7 text-muted-foreground hover:text-destructive"
                                                    onClick={() => deleteTx.mutate(tx.id)}
                                                >
                                                    <Trash2 className="h-3.5 w-3.5" />
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                        {data?.total ?? 0} transações · Página {filters.page} de {totalPages}
                    </span>
                    <div className="flex items-center gap-1">
                        <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            disabled={(filters.page ?? 1) <= 1}
                            onClick={() =>
                                setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))
                            }
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            disabled={(filters.page ?? 1) >= totalPages}
                            onClick={() =>
                                setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))
                            }
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
}
