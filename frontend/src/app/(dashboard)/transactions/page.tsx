"use client";

import { useState, useMemo } from "react";
import {
  useTransactions,
  useCreateTransaction,
  useDeleteTransaction,
  useAccounts,
  useCategories,
  type CreateTransactionPayload,
} from "@/hooks";
import { formatCurrency, formatDate } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
import { Plus, Trash2, Receipt } from "lucide-react";

const PAGE_SIZE = 10;

export default function TransactionsPage() {
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [filterAccount, setFilterAccount] = useState("all");
  const [filterType, setFilterType] = useState<"all" | "income" | "expense">("all");
  const [open, setOpen] = useState(false);

  const [form, setForm] = useState<CreateTransactionPayload>({
    description: "",
    amount: 0,
    type: "expense",
    date: new Date().toISOString().slice(0, 10),
    account_id: "",
    category_id: undefined,
  });

  const { data: transactions, isLoading } = useTransactions({
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    account_id: filterAccount !== "all" ? filterAccount : undefined,
    type: filterType !== "all" ? filterType : undefined,
  });

  const { data: accounts } = useAccounts();
  const { data: categories } = useCategories();
  const createTransaction = useCreateTransaction();
  const deleteTransaction = useDeleteTransaction();

  const filtered = useMemo(() => {
    if (!transactions) return [];
    if (!search) return transactions;
    const q = search.toLowerCase();
    return transactions.filter((t) =>
      t.description.toLowerCase().includes(q)
    );
  }, [transactions, search]);

  const paginated = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);

  function accountName(id: string) {
    return accounts?.find((a) => a.id === id)?.name ?? id;
  }

  function categoryName(id?: string) {
    if (!id) return "—";
    return categories?.find((c) => c.id === id)?.name ?? id;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await createTransaction.mutateAsync(form);
    setOpen(false);
    setForm({
      description: "",
      amount: 0,
      type: "expense",
      date: new Date().toISOString().slice(0, 10),
      account_id: "",
      category_id: undefined,
    });
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Transações</h1>
          <p className="text-sm text-gray-500">Gerencie suas receitas e despesas</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nova transação
            </Button>
          </DialogTrigger>
          <DialogPortal>
            <DialogBackdrop />
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Nova Transação</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="description">Descrição</Label>
                  <Input
                    id="description"
                    required
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="amount">Valor (R$)</Label>
                    <Input
                      id="amount"
                      type="number"
                      min="0.01"
                      step="0.01"
                      required
                      value={form.amount || ""}
                      onChange={(e) => setForm({ ...form, amount: parseFloat(e.target.value) })}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="date">Data</Label>
                    <Input
                      id="date"
                      type="date"
                      required
                      value={form.date}
                      onChange={(e) => setForm({ ...form, date: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <Label>Tipo</Label>
                  <Select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value as "income" | "expense" })}
                  >
                    <SelectItem value="income">Receita</SelectItem>
                    <SelectItem value="expense">Despesa</SelectItem>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label>Conta</Label>
                  <Select
                    value={form.account_id}
                    onChange={(e) => setForm({ ...form, account_id: e.target.value })}
                  >
                    <SelectItem value="">Selecione uma conta</SelectItem>
                    {accounts?.map((a) => (
                      <SelectItem key={a.id} value={a.id}>
                        {a.name}
                      </SelectItem>
                    ))}
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label>Categoria (opcional)</Label>
                  <Select
                    value={form.category_id ?? "none"}
                    onChange={(e) =>
                      setForm({ ...form, category_id: e.target.value === "none" ? undefined : e.target.value })
                    }
                  >
                    <SelectItem value="none">Sem categoria</SelectItem>
                    {categories?.map((c) => (
                      <SelectItem key={c.id} value={c.id}>
                        {c.name}
                      </SelectItem>
                    ))}
                  </Select>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                    Cancelar
                  </Button>
                  <Button type="submit" disabled={createTransaction.isPending}>
                    {createTransaction.isPending ? "Salvando..." : "Salvar"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </DialogPortal>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 rounded-lg border bg-white p-4">
        <div className="flex items-center gap-2">
          <Label className="text-xs text-gray-500">De</Label>
          <Input
            type="date"
            className="h-8 w-36 text-sm"
            value={dateFrom}
            onChange={(e) => { setDateFrom(e.target.value); setPage(0); }}
          />
        </div>
        <div className="flex items-center gap-2">
          <Label className="text-xs text-gray-500">Até</Label>
          <Input
            type="date"
            className="h-8 w-36 text-sm"
            value={dateTo}
            onChange={(e) => { setDateTo(e.target.value); setPage(0); }}
          />
        </div>
        <Select
          value={filterAccount}
          onChange={(e) => { setFilterAccount(e.target.value); setPage(0); }}
          className="h-8 w-44 text-sm"
        >
          <SelectItem value="all">Todas as contas</SelectItem>
          {accounts?.map((a) => (
            <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
          ))}
        </Select>
        <Select
          value={filterType}
          onChange={(e) => { setFilterType(e.target.value as "all" | "income" | "expense"); setPage(0); }}
          className="h-8 w-36 text-sm"
        >
          <SelectItem value="all">Todas</SelectItem>
          <SelectItem value="income">Receita</SelectItem>
          <SelectItem value="expense">Despesa</SelectItem>
        </Select>
        <Input
          placeholder="Buscar descrição..."
          className="h-8 w-48 text-sm"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0); }}
        />
      </div>

      {/* Table */}
      <div className="rounded-lg border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Categoria</TableHead>
              <TableHead>Conta</TableHead>
              <TableHead className="text-right">Valor</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : paginated.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="py-16 text-center">
                  <div className="flex flex-col items-center gap-2 text-gray-400">
                    <Receipt className="h-10 w-10 opacity-30" />
                    <p className="text-sm font-medium">Nenhuma transação encontrada</p>
                    <p className="text-xs">Ajuste os filtros ou adicione uma nova transação</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              paginated.map((t) => (
                <TableRow key={t.id}>
                  <TableCell className="text-sm text-gray-600">{formatDate(t.date)}</TableCell>
                  <TableCell className="font-medium">{t.description}</TableCell>
                  <TableCell className="text-sm text-gray-600">{categoryName(t.category_id)}</TableCell>
                  <TableCell className="text-sm text-gray-600">{accountName(t.account_id)}</TableCell>
                  <TableCell className={`text-right font-semibold ${t.type === "income" ? "text-green-600" : "text-red-600"}`}>
                    {t.type === "expense" ? "- " : "+ "}
                    {formatCurrency(t.amount)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={t.type === "income" ? "default" : "destructive"} className={t.type === "income" ? "bg-green-100 text-green-700 hover:bg-green-100" : ""}>
                      {t.type === "income" ? "Receita" : "Despesa"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-gray-400 hover:text-red-500"
                      onClick={() => deleteTransaction.mutate(t.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, filtered.length)} de {filtered.length}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 0}
              onClick={() => setPage(page - 1)}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page + 1 >= totalPages}
              onClick={() => setPage(page + 1)}
            >
              Próximo
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
