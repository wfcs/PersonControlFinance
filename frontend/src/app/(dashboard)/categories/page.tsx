"use client";

import { useState } from "react";
import {
  useCategories,
  useCreateCategory,
  useDeleteCategory,
  type CreateCategoryPayload,
} from "@/hooks";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { Plus, Trash2, Tag } from "lucide-react";

export default function CategoriesPage() {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<CreateCategoryPayload>({
    name: "",
    type: "expense",
    color: "#6366f1",
    icon: "",
  });

  const { data: categories, isLoading } = useCategories();
  const createCategory = useCreateCategory();
  const deleteCategory = useDeleteCategory();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await createCategory.mutateAsync(form);
    setOpen(false);
    setForm({ name: "", type: "expense", color: "#6366f1", icon: "" });
  }

  const incomeCategories = categories?.filter((c) => c.type === "income") ?? [];
  const expenseCategories = categories?.filter((c) => c.type === "expense") ?? [];

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Categorias</h1>
          <p className="text-sm text-gray-500">Organize suas transações por categoria</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nova categoria
            </Button>
          </DialogTrigger>
          <DialogPortal>
            <DialogBackdrop />
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Nova Categoria</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="cat-name">Nome</Label>
                  <Input
                    id="cat-name"
                    required
                    placeholder="Ex: Alimentação, Salário..."
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Tipo</Label>
                  <Select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value as "income" | "expense" })}
                  >
                    <SelectItem value="expense">Despesa</SelectItem>
                    <SelectItem value="income">Receita</SelectItem>
                  </Select>
                </div>
              <div className="space-y-1.5">
                <Label htmlFor="cat-color">Cor</Label>
                <div className="flex items-center gap-3">
                  <input
                    id="cat-color"
                    type="color"
                    className="h-9 w-14 cursor-pointer rounded border p-1"
                    value={form.color ?? "#6366f1"}
                    onChange={(e) => setForm({ ...form, color: e.target.value })}
                  />
                  <Input
                    value={form.color ?? ""}
                    onChange={(e) => setForm({ ...form, color: e.target.value })}
                    placeholder="#6366f1"
                    className="flex-1"
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="cat-icon">Ícone (emoji ou texto)</Label>
                <Input
                  id="cat-icon"
                  placeholder="Ex: 🍔, 💰, 🏠"
                  value={form.icon ?? ""}
                  onChange={(e) => setForm({ ...form, icon: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={createCategory.isPending}>
                  {createCategory.isPending ? "Salvando..." : "Salvar"}
                </Button>
              </div>
              </form>
            </DialogContent>
          </DialogPortal>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-lg" />
          ))}
        </div>
      ) : !categories || categories.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-20 text-center">
          <Tag className="mb-4 h-12 w-12 text-gray-300" />
          <h3 className="text-base font-semibold text-gray-700">Nenhuma categoria</h3>
          <p className="mb-4 text-sm text-gray-400">Crie categorias para organizar suas transações</p>
          <Button onClick={() => setOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nova categoria
          </Button>
        </div>
      ) : (
        <div className="space-y-6">
          {expenseCategories.length > 0 && (
            <div>
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
                Despesas ({expenseCategories.length})
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {expenseCategories.map((cat) => (
                  <div key={cat.id} className="flex items-center justify-between rounded-lg border bg-white px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div
                        className="flex h-9 w-9 items-center justify-center rounded-full text-lg"
                        style={{ backgroundColor: `${cat.color ?? "#6366f1"}20` }}
                      >
                        {cat.icon ? (
                          <span>{cat.icon}</span>
                        ) : (
                          <div className="h-4 w-4 rounded-full" style={{ backgroundColor: cat.color ?? "#6366f1" }} />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{cat.name}</p>
                        <Badge variant="secondary" className="mt-0.5 bg-red-50 text-xs text-red-600">
                          Despesa
                        </Badge>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-gray-400 hover:text-red-500"
                      onClick={() => deleteCategory.mutate(cat.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {incomeCategories.length > 0 && (
            <div>
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
                Receitas ({incomeCategories.length})
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {incomeCategories.map((cat) => (
                  <div key={cat.id} className="flex items-center justify-between rounded-lg border bg-white px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div
                        className="flex h-9 w-9 items-center justify-center rounded-full text-lg"
                        style={{ backgroundColor: `${cat.color ?? "#22c55e"}20` }}
                      >
                        {cat.icon ? (
                          <span>{cat.icon}</span>
                        ) : (
                          <div className="h-4 w-4 rounded-full" style={{ backgroundColor: cat.color ?? "#22c55e" }} />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{cat.name}</p>
                        <Badge variant="secondary" className="mt-0.5 bg-green-50 text-xs text-green-600">
                          Receita
                        </Badge>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-gray-400 hover:text-red-500"
                      onClick={() => deleteCategory.mutate(cat.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
