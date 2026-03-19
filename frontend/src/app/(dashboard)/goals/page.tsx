"use client";

import { useState } from "react";
import {
  useGoals,
  useCreateGoal,
  useUpdateGoal,
  useDeleteGoal,
  type CreateGoalPayload,
} from "@/hooks";
import { formatCurrency, formatDate, formatPercentage } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogPortal,
  DialogBackdrop,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Trash2, Target, Pencil, Check, X } from "lucide-react";

export default function GoalsPage() {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<CreateGoalPayload>({
    name: "",
    target_amount: 0,
    current_amount: 0,
    deadline: "",
    description: "",
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editAmount, setEditAmount] = useState("");

  const { data: goals, isLoading } = useGoals();
  const createGoal = useCreateGoal();
  const updateGoal = useUpdateGoal();
  const deleteGoal = useDeleteGoal();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await createGoal.mutateAsync(form);
    setOpen(false);
    setForm({ name: "", target_amount: 0, current_amount: 0, deadline: "", description: "" });
  }

  async function handleUpdateAmount(id: string) {
    const amount = parseFloat(editAmount);
    if (isNaN(amount)) return;
    await updateGoal.mutateAsync({ id, current_amount: amount });
    setEditingId(null);
    setEditAmount("");
  }

  function goalStatus(current: number, target: number, deadline?: string) {
    const pct = (current / target) * 100;
    if (pct >= 100) return { label: "Concluída", cls: "bg-green-100 text-green-700" };
    if (deadline && new Date(deadline) < new Date()) return { label: "Atrasada", cls: "bg-red-100 text-red-700" };
    return { label: "Em andamento", cls: "bg-blue-100 text-blue-700" };
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Metas</h1>
          <p className="text-sm text-gray-500">Acompanhe o progresso dos seus objetivos financeiros</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nova meta
            </Button>
          </DialogTrigger>
          <DialogPortal>
            <DialogBackdrop />
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Nova Meta</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="goal-name">Nome da meta</Label>
                <Input
                  id="goal-name"
                  required
                  placeholder="Ex: Reserva de emergência, Viagem..."
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="target-amount">Valor alvo (R$)</Label>
                  <Input
                    id="target-amount"
                    type="number"
                    min="0.01"
                    step="0.01"
                    required
                    value={form.target_amount || ""}
                    onChange={(e) => setForm({ ...form, target_amount: parseFloat(e.target.value) })}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="current-amount">Valor atual (R$)</Label>
                  <Input
                    id="current-amount"
                    type="number"
                    min="0"
                    step="0.01"
                    value={form.current_amount ?? ""}
                    onChange={(e) => setForm({ ...form, current_amount: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="deadline">Prazo (opcional)</Label>
                <Input
                  id="deadline"
                  type="date"
                  value={form.deadline ?? ""}
                  onChange={(e) => setForm({ ...form, deadline: e.target.value })}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="goal-desc">Descrição (opcional)</Label>
                <Input
                  id="goal-desc"
                  placeholder="Detalhes sobre a meta..."
                  value={form.description ?? ""}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={createGoal.isPending}>
                  {createGoal.isPending ? "Salvando..." : "Salvar"}
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
            <Skeleton key={i} className="h-48 rounded-xl" />
          ))}
        </div>
      ) : !goals || goals.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-20 text-center">
          <Target className="mb-4 h-12 w-12 text-gray-300" />
          <h3 className="text-base font-semibold text-gray-700">Nenhuma meta cadastrada</h3>
          <p className="mb-4 text-sm text-gray-400">Defina metas financeiras para alcançar seus objetivos</p>
          <Button onClick={() => setOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Criar primeira meta
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {goals.map((goal) => {
            const pct = Math.min((goal.current_amount / goal.target_amount) * 100, 100);
            const status = goalStatus(goal.current_amount, goal.target_amount, goal.deadline);
            const remaining = goal.target_amount - goal.current_amount;

            return (
              <Card key={goal.id} className="flex flex-col">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base leading-tight">{goal.name}</CardTitle>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-gray-400 hover:text-blue-500"
                        onClick={() => {
                          setEditingId(goal.id);
                          setEditAmount(String(goal.current_amount));
                        }}
                      >
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-gray-400 hover:text-red-500"
                        onClick={() => deleteGoal.mutate(goal.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                  <Badge className={`w-fit text-xs ${status.cls}`} variant="secondary">
                    {status.label}
                  </Badge>
                </CardHeader>
                <CardContent className="flex flex-1 flex-col gap-3">
                  {goal.description && (
                    <p className="text-xs text-gray-400">{goal.description}</p>
                  )}

                  <div>
                    <div className="mb-1 flex justify-between text-xs text-gray-500">
                      <span>{formatCurrency(goal.current_amount)}</span>
                      <span>{formatCurrency(goal.target_amount)}</span>
                    </div>
                    <Progress value={pct} className="h-2" />
                    <p className="mt-1 text-right text-xs text-gray-500">
                      {formatPercentage(pct)} concluído
                    </p>
                  </div>

                  {remaining > 0 && (
                    <p className="text-xs text-gray-500">
                      Faltam <span className="font-medium text-gray-700">{formatCurrency(remaining)}</span>
                    </p>
                  )}

                  {goal.deadline && (
                    <p className="text-xs text-gray-500">
                      Prazo: <span className="font-medium">{formatDate(goal.deadline)}</span>
                    </p>
                  )}

                  {editingId === goal.id ? (
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        className="h-8 text-sm"
                        placeholder="Valor atual"
                        value={editAmount}
                        onChange={(e) => setEditAmount(e.target.value)}
                        autoFocus
                      />
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-8 w-8 text-green-600"
                        onClick={() => handleUpdateAmount(goal.id)}
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-8 w-8 text-gray-400"
                        onClick={() => setEditingId(null)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : null}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
