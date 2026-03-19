"use client";

import { useState } from "react";
import {
  useAccounts,
  useCreateAccount,
  useDeleteAccount,
  type CreateAccountPayload,
} from "@/hooks";
import { formatCurrency } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogPortal,
  DialogBackdrop,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectItem,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Trash2, Wallet, Building2 } from "lucide-react";

const ACCOUNT_TYPES: Record<string, string> = {
  checking: "Corrente",
  savings: "Poupança",
  investment: "Investimento",
  credit: "Crédito",
  cash: "Dinheiro",
  other: "Outro",
};

export default function AccountsPage() {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<CreateAccountPayload & { bank_name?: string }>({
    name: "",
    type: "checking",
    balance: 0,
    currency: "BRL",
  });

  const { data: accounts, isLoading } = useAccounts();
  const createAccount = useCreateAccount();
  const deleteAccount = useDeleteAccount();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await createAccount.mutateAsync({
      name: form.name,
      type: form.type,
      balance: form.balance,
      currency: form.currency,
    });
    setOpen(false);
    setForm({ name: "", type: "checking", balance: 0, currency: "BRL" });
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Contas</h1>
          <p className="text-sm text-gray-500">Gerencie suas contas bancárias e carteiras</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Adicionar conta
            </Button>
          </DialogTrigger>
          <DialogPortal>
            <DialogBackdrop />
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Nova Conta</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="name">Nome da conta</Label>
                  <Input
                    id="name"
                    required
                    placeholder="Ex: Nubank, Itaú..."
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Tipo</Label>
                  <Select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value })}
                  >
                    {Object.entries(ACCOUNT_TYPES).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </Select>
                </div>
              <div className="space-y-1.5">
                <Label htmlFor="bank_name">Banco (opcional)</Label>
                <Input
                  id="bank_name"
                  placeholder="Ex: Nubank, Itaú, Bradesco..."
                  value={form.bank_name ?? ""}
                  onChange={(e) => setForm({ ...form, bank_name: e.target.value })}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="balance">Saldo inicial (R$)</Label>
                <Input
                  id="balance"
                  type="number"
                  step="0.01"
                  value={form.balance ?? ""}
                  onChange={(e) => setForm({ ...form, balance: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={createAccount.isPending}>
                  {createAccount.isPending ? "Salvando..." : "Salvar"}
                </Button>
              </div>
              </form>
            </DialogContent>
          </DialogPortal>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-40 rounded-xl" />
          ))}
        </div>
      ) : accounts && accounts.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {accounts.map((account) => (
            <Card key={account.id} className="relative overflow-hidden">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100">
                      <Wallet className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{account.name}</CardTitle>
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Building2 className="h-3 w-3" />
                        <span>{account.currency}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-gray-400 hover:text-red-500"
                    onClick={() => deleteAccount.mutate(account.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="mt-1 flex items-end justify-between">
                  <div>
                    <p className="text-xs text-gray-500">Saldo atual</p>
                    <p className={`text-xl font-bold ${account.balance >= 0 ? "text-gray-900" : "text-red-600"}`}>
                      {formatCurrency(account.balance)}
                    </p>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {ACCOUNT_TYPES[account.type] ?? account.type}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-20 text-center">
          <Wallet className="mb-4 h-12 w-12 text-gray-300" />
          <h3 className="text-base font-semibold text-gray-700">Nenhuma conta cadastrada</h3>
          <p className="mb-4 text-sm text-gray-400">Adicione sua primeira conta para começar</p>
          <Button onClick={() => setOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Adicionar conta
          </Button>
        </div>
      )}
    </div>
  );
}
