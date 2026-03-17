"use client";

import { useState } from "react";
import { useAccounts, useCreateAccount, type AccountCreate } from "@/hooks/use-accounts";
import { Card, CardContent } from "@/components/ui/card";
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
import { formatCurrency } from "@/lib/format";
import {
    Plus,
    Building2,
    CreditCard,
    Wallet,
    Landmark,
    Banknote,
    Wifi,
    WifiOff,
} from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const accountSchema = z.object({
    name: z.string().min(1, "Nome obrigatório"),
    institution_name: z.string().min(1, "Instituição obrigatória"),
    type: z.enum(["checking", "savings", "credit_card", "investment", "cash"]),
    balance: z.coerce.number().default(0),
    credit_limit: z.coerce.number().optional(),
});

type AccForm = z.infer<typeof accountSchema>;

const typeIcons: Record<string, React.ReactNode> = {
    checking: <Landmark className="h-5 w-5" />,
    savings: <Banknote className="h-5 w-5" />,
    credit_card: <CreditCard className="h-5 w-5" />,
    investment: <Building2 className="h-5 w-5" />,
    cash: <Wallet className="h-5 w-5" />,
};

const typeLabels: Record<string, string> = {
    checking: "Conta Corrente",
    savings: "Poupança",
    credit_card: "Cartão de Crédito",
    investment: "Investimento",
    cash: "Dinheiro",
};

const typeColors: Record<string, string> = {
    checking: "bg-blue-50 text-blue-600",
    savings: "bg-emerald-50 text-emerald-600",
    credit_card: "bg-purple-50 text-purple-600",
    investment: "bg-amber-50 text-amber-600",
    cash: "bg-gray-50 text-gray-600",
};

export default function AccountsPage() {
    const { data: accounts, isLoading } = useAccounts();
    const createAccount = useCreateAccount();
    const [dialogOpen, setDialogOpen] = useState(false);

    const {
        register,
        handleSubmit,
        reset,
        setValue,
        watch,
        formState: { errors, isSubmitting },
    } = useForm<AccForm>({ resolver: zodResolver(accountSchema) as any });

    const watchType = watch("type");

    const onSubmit = async (values: AccForm) => {
        const body: AccountCreate = {
            ...values,
            credit_limit: values.type === "credit_card" ? values.credit_limit : undefined,
        };
        await createAccount.mutateAsync(body);
        reset();
        setDialogOpen(false);
    };

    const totalBalance = (accounts ?? [])
        .filter((a) => a.is_active && a.type !== "credit_card")
        .reduce((sum, a) => sum + Number(a.balance), 0);

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm text-muted-foreground">Saldo total</p>
                    {isLoading ? (
                        <Skeleton className="h-8 w-40 mt-1" />
                    ) : (
                        <p className="text-2xl font-bold tabular-nums">
                            {formatCurrency(totalBalance)}
                        </p>
                    )}
                </div>

                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    {/* @ts-expect-error asChild Radix compatibility */}
                    <DialogTrigger asChild>
                        <Button size="sm">
                            <Plus className="h-4 w-4 mr-1.5" />
                            Adicionar conta
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[420px]">
                        <DialogHeader>
                            <DialogTitle>Nova Conta</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-2">
                            <div className="space-y-2">
                                <Label>Nome da conta</Label>
                                <Input placeholder="Ex: Nubank" {...register("name")} />
                                {errors.name && (
                                    <p className="text-destructive text-xs">{errors.name.message}</p>
                                )}
                            </div>
                            <div className="space-y-2">
                                <Label>Instituição</Label>
                                <Input placeholder="Ex: Nu Pagamentos" {...register("institution_name")} />
                                {errors.institution_name && (
                                    <p className="text-destructive text-xs">{errors.institution_name.message}</p>
                                )}
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-2">
                                    <Label>Tipo</Label>
                                    <Select onValueChange={(v) => setValue("type", v as AccForm["type"])}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Selecione" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="checking">Conta Corrente</SelectItem>
                                            <SelectItem value="savings">Poupança</SelectItem>
                                            <SelectItem value="credit_card">Cartão de Crédito</SelectItem>
                                            <SelectItem value="investment">Investimento</SelectItem>
                                            <SelectItem value="cash">Dinheiro</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    {errors.type && (
                                        <p className="text-destructive text-xs">{errors.type.message}</p>
                                    )}
                                </div>
                                <div className="space-y-2">
                                    <Label>Saldo inicial (R$)</Label>
                                    <Input type="number" step="0.01" placeholder="0,00" {...register("balance")} />
                                </div>
                            </div>
                            {watchType === "credit_card" && (
                                <div className="space-y-2">
                                    <Label>Limite do cartão (R$)</Label>
                                    <Input
                                        type="number"
                                        step="0.01"
                                        placeholder="0,00"
                                        {...register("credit_limit")}
                                    />
                                </div>
                            )}
                            <Button type="submit" className="w-full" disabled={isSubmitting}>
                                Salvar
                            </Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Cards Grid */}
            {isLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-[140px]" />
                    ))}
                </div>
            ) : (accounts ?? []).length === 0 ? (
                <Card>
                    <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                        <Wallet className="h-10 w-10 text-muted-foreground mb-3" />
                        <p className="text-muted-foreground text-sm">
                            Nenhuma conta cadastrada
                        </p>
                        <Button
                            size="sm"
                            className="mt-3"
                            onClick={() => setDialogOpen(true)}
                        >
                            <Plus className="h-4 w-4 mr-1.5" />
                            Adicionar primeira conta
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {accounts!.map((acc) => {
                        const color = typeColors[acc.type] ?? typeColors.cash;
                        const icon = typeIcons[acc.type] ?? typeIcons.cash;
                        const label = typeLabels[acc.type] ?? acc.type;

                        return (
                            <Card
                                key={acc.id}
                                className="hover:shadow-md transition-shadow relative overflow-hidden"
                            >
                                <CardContent className="pt-5">
                                    <div className="flex items-start justify-between mb-3">
                                        <div className={`p-2 rounded-lg ${color}`}>{icon}</div>
                                        <div className="flex items-center gap-1.5">
                                            {acc.pluggy_item_id ? (
                                                <Badge
                                                    variant="secondary"
                                                    className="text-[10px] gap-1 bg-emerald-50 text-emerald-600 border-0"
                                                >
                                                    <Wifi className="h-3 w-3" />
                                                    Conectada
                                                </Badge>
                                            ) : (
                                                <Badge
                                                    variant="secondary"
                                                    className="text-[10px] gap-1"
                                                >
                                                    <WifiOff className="h-3 w-3" />
                                                    Manual
                                                </Badge>
                                            )}
                                            {!acc.is_active && (
                                                <Badge variant="destructive" className="text-[10px]">
                                                    Inativa
                                                </Badge>
                                            )}
                                        </div>
                                    </div>
                                    <p className="font-semibold text-sm">{acc.name}</p>
                                    <p className="text-xs text-muted-foreground mb-3">
                                        {acc.institution_name} · {label}
                                    </p>
                                    <p className="text-xl font-bold tabular-nums">
                                        {formatCurrency(Number(acc.balance))}
                                    </p>
                                    {acc.credit_limit && (
                                        <div className="mt-2">
                                            <div className="flex justify-between text-xs text-muted-foreground mb-1">
                                                <span>Utilizado</span>
                                                <span>Limite: {formatCurrency(Number(acc.credit_limit))}</span>
                                            </div>
                                            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-primary rounded-full transition-all"
                                                    style={{
                                                        width: `${Math.min(100, (Math.abs(Number(acc.balance)) / Number(acc.credit_limit)) * 100)}%`,
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
