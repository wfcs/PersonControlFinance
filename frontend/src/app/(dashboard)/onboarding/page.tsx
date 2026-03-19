"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCreateAccount } from "@/hooks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectItem,
} from "@/components/ui/select";
import { Wallet, Target, PartyPopper, CheckCircle2, Circle } from "lucide-react";

const FINANCIAL_GOALS = [
  { id: "emergency", label: "Criar reserva de emergência", icon: "🛡️" },
  { id: "debt", label: "Quitar dívidas", icon: "💳" },
  { id: "invest", label: "Começar a investir", icon: "📈" },
  { id: "travel", label: "Economizar para viagem", icon: "✈️" },
  { id: "house", label: "Comprar imóvel", icon: "🏠" },
  { id: "retirement", label: "Planejar aposentadoria", icon: "🌴" },
  { id: "education", label: "Educação / curso", icon: "🎓" },
  { id: "car", label: "Comprar carro", icon: "🚗" },
];

const ACCOUNT_TYPES: Record<string, string> = {
  checking: "Conta Corrente",
  savings: "Poupança",
  investment: "Investimento",
  cash: "Dinheiro em espécie",
};

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [accountForm, setAccountForm] = useState({
    name: "",
    type: "checking",
    balance: 0,
  });
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const createAccount = useCreateAccount();

  const TOTAL_STEPS = 3;
  const progress = ((step - 1) / (TOTAL_STEPS - 1)) * 100;

  function toggleGoal(id: string) {
    setSelectedGoals((prev) =>
      prev.includes(id) ? prev.filter((g) => g !== id) : [...prev, id]
    );
  }

  async function handleCreateAccount(e: React.FormEvent) {
    e.preventDefault();
    if (accountForm.name) {
      await createAccount.mutateAsync({
        name: accountForm.name,
        type: accountForm.type,
        balance: accountForm.balance,
        currency: "BRL",
      });
    }
    setStep(3);
  }

  function handleFinish() {
    router.push("/dashboard");
  }

  return (
    <div className="mx-auto max-w-lg p-6">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="mb-2 flex justify-between text-xs text-gray-400">
          <span>Passo {step} de {TOTAL_STEPS}</span>
          <span>{Math.round(progress)}% concluído</span>
        </div>
        <Progress value={progress} className="h-2" />
        <div className="mt-3 flex justify-between">
          {[
            { n: 1, label: "Boas-vindas" },
            { n: 2, label: "Primeira conta" },
            { n: 3, label: "Metas" },
          ].map(({ n, label }) => (
            <div key={n} className="flex flex-col items-center gap-1">
              <div className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                n < step ? "bg-green-500 text-white" : n === step ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-400"
              }`}>
                {n < step ? <CheckCircle2 className="h-4 w-4" /> : n}
              </div>
              <span className={`text-xs ${n === step ? "font-medium text-blue-600" : "text-gray-400"}`}>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Step 1: Welcome */}
      {step === 1 && (
        <div className="space-y-6 text-center">
          <div className="flex justify-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-blue-100">
              <PartyPopper className="h-10 w-10 text-blue-600" />
            </div>
          </div>
          <div>
            <h1 className="text-2xl font-bold">Bem-vindo ao FinApp!</h1>
            <p className="mt-2 text-gray-500">
              Vamos configurar sua conta em poucos minutos para que você possa começar a organizar suas finanças.
            </p>
          </div>
          <div className="rounded-lg border bg-blue-50 p-4 text-left">
            <h3 className="mb-2 text-sm font-semibold text-blue-700">O que você vai poder fazer:</h3>
            <ul className="space-y-1.5 text-sm text-blue-600">
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> Acompanhar receitas e despesas</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> Definir e acompanhar metas financeiras</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> Visualizar relatórios e gráficos</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" /> Projetar seu saldo futuro</li>
            </ul>
          </div>
          <Button size="lg" className="w-full" onClick={() => setStep(2)}>
            Começar configuração
          </Button>
        </div>
      )}

      {/* Step 2: First account */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                <Wallet className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h2 className="text-xl font-bold">Adicione sua primeira conta</h2>
            <p className="mt-1 text-sm text-gray-500">
              Comece cadastrando uma conta bancária ou carteira
            </p>
          </div>

          <form onSubmit={handleCreateAccount} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="acc-name">Nome da conta</Label>
              <Input
                id="acc-name"
                placeholder="Ex: Nubank, Itaú, Carteira..."
                required
                value={accountForm.name}
                onChange={(e) => setAccountForm({ ...accountForm, name: e.target.value })}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Tipo de conta</Label>
              <Select
                value={accountForm.type}
                onChange={(e) => setAccountForm({ ...accountForm, type: e.target.value })}
              >
                {Object.entries(ACCOUNT_TYPES).map(([value, label]) => (
                  <SelectItem key={value} value={value}>{label}</SelectItem>
                ))}
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="acc-balance">Saldo atual (R$)</Label>
              <Input
                id="acc-balance"
                type="number"
                step="0.01"
                min="0"
                placeholder="0,00"
                value={accountForm.balance || ""}
                onChange={(e) => setAccountForm({ ...accountForm, balance: parseFloat(e.target.value) || 0 })}
              />
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={() => setStep(3)}>
                Pular por agora
              </Button>
              <Button type="submit" className="flex-1" disabled={createAccount.isPending}>
                {createAccount.isPending ? "Salvando..." : "Continuar"}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Step 3: Goals */}
      {step === 3 && (
        <div className="space-y-6">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
                <Target className="h-8 w-8 text-purple-600" />
              </div>
            </div>
            <h2 className="text-xl font-bold">Quais são seus objetivos?</h2>
            <p className="mt-1 text-sm text-gray-500">
              Selecione os objetivos financeiros que deseja alcançar
            </p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {FINANCIAL_GOALS.map((goal) => {
              const selected = selectedGoals.includes(goal.id);
              return (
                <button
                  key={goal.id}
                  type="button"
                  onClick={() => toggleGoal(goal.id)}
                  className={`flex items-center gap-2 rounded-lg border p-3 text-left text-sm transition-colors ${
                    selected
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  <span className="text-lg">{goal.icon}</span>
                  <span className="font-medium leading-tight">{goal.label}</span>
                  <div className="ml-auto">
                    {selected ? (
                      <CheckCircle2 className="h-4 w-4 text-blue-500" />
                    ) : (
                      <Circle className="h-4 w-4 text-gray-300" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {selectedGoals.length > 0 && (
            <p className="text-center text-xs text-blue-600">
              {selectedGoals.length} objetivo(s) selecionado(s)
            </p>
          )}

          <Button size="lg" className="w-full" onClick={handleFinish}>
            Concluir configuração
          </Button>
          <p className="text-center text-xs text-gray-400">
            Você pode ajustar suas metas a qualquer momento nas configurações
          </p>
        </div>
      )}
    </div>
  );
}
