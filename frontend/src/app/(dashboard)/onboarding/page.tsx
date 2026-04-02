"use client";

import { useState } from "react";
import { useCompleteOnboarding } from "@/hooks/use-auth";
import { usePluggyStatus } from "@/hooks/use-open-finance";
import { PluggyConnectButton } from "@/components/open-finance/pluggy-connect-widget";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  PartyPopper,
  CheckCircle2,
  Link2,
  Target,
  Circle,
  ShieldCheck,
} from "lucide-react";

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

export default function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const completeOnboarding = useCompleteOnboarding();
  const { data: pluggyStatus, refetch: refetchPluggy } = usePluggyStatus();

  const TOTAL_STEPS = 3;
  const progress = ((step - 1) / (TOTAL_STEPS - 1)) * 100;

  const hasConnectedBank = (pluggyStatus?.connected_items ?? 0) > 0;

  function toggleGoal(id: string) {
    setSelectedGoals((prev) =>
      prev.includes(id) ? prev.filter((g) => g !== id) : [...prev, id]
    );
  }

  function handleFinish() {
    completeOnboarding.mutate();
  }

  return (
    <div className="mx-auto max-w-lg p-6">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="mb-2 flex justify-between text-xs text-gray-400">
          <span>
            Passo {step} de {TOTAL_STEPS}
          </span>
          <span>{Math.round(progress)}% concluído</span>
        </div>
        <Progress value={progress} className="h-2" />
        <div className="mt-3 flex justify-between">
          {[
            { n: 1, label: "Boas-vindas" },
            { n: 2, label: "Conectar banco" },
            { n: 3, label: "Metas" },
          ].map(({ n, label }) => (
            <div key={n} className="flex flex-col items-center gap-1">
              <div
                className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                  n < step
                    ? "bg-green-500 text-white"
                    : n === step
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                {n < step ? <CheckCircle2 className="h-4 w-4" /> : n}
              </div>
              <span
                className={`text-xs ${
                  n === step
                    ? "font-medium text-blue-600"
                    : "text-gray-400"
                }`}
              >
                {label}
              </span>
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
            <h1 className="text-2xl font-bold">Bem-vindo ao FinControl!</h1>
            <p className="mt-2 text-gray-500">
              Vamos configurar sua conta em poucos minutos para que você possa
              começar a organizar suas finanças.
            </p>
          </div>
          <div className="rounded-lg border bg-blue-50 p-4 text-left">
            <h3 className="mb-2 text-sm font-semibold text-blue-700">
              O que você vai poder fazer:
            </h3>
            <ul className="space-y-1.5 text-sm text-blue-600">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" /> Importar
                contas e transações automaticamente
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" /> Acompanhar
                receitas e despesas em tempo real
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" /> Definir e
                acompanhar metas financeiras
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" /> Visualizar
                relatórios e gráficos detalhados
              </li>
            </ul>
          </div>
          <Button size="lg" className="w-full" onClick={() => setStep(2)}>
            Começar configuração
          </Button>
        </div>
      )}

      {/* Step 2: Connect bank via Open Finance (mandatory) */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                <Link2 className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h2 className="text-xl font-bold">Conecte seu banco</h2>
            <p className="mt-1 text-sm text-gray-500">
              Conecte sua conta bancária via Open Finance para importar seus
              dados automaticamente
            </p>
          </div>

          <div className="rounded-lg border bg-green-50 p-4">
            <div className="flex items-start gap-3">
              <ShieldCheck className="h-5 w-5 text-green-600 mt-0.5 shrink-0" />
              <div className="text-sm text-green-700">
                <p className="font-semibold mb-1">Conexão segura</p>
                <p>
                  Seus dados são criptografados e protegidos. Usamos a
                  tecnologia Open Finance regulada pelo Banco Central.
                </p>
              </div>
            </div>
          </div>

          {hasConnectedBank ? (
            <div className="space-y-4">
              <div className="rounded-lg border border-green-300 bg-green-50 p-4 text-center">
                <CheckCircle2 className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <p className="text-sm font-semibold text-green-700">
                  Banco conectado com sucesso!
                </p>
                <p className="text-xs text-green-600 mt-1">
                  Suas contas e transações estão sendo importadas
                </p>
              </div>
              <Button
                size="lg"
                className="w-full"
                onClick={() => setStep(3)}
              >
                Continuar
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-center">
                <PluggyConnectButton />
              </div>
              <Button
                size="lg"
                variant="ghost"
                className="w-full text-gray-400"
                onClick={async () => {
                  await refetchPluggy();
                }}
              >
                Já conectei, verificar novamente
              </Button>
              <p className="text-center text-xs text-gray-400">
                A conexão bancária é necessária para usar o FinControl
              </p>
            </div>
          )}
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
                  <span className="font-medium leading-tight">
                    {goal.label}
                  </span>
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

          <Button
            size="lg"
            className="w-full"
            onClick={handleFinish}
            disabled={completeOnboarding.isPending}
          >
            {completeOnboarding.isPending
              ? "Finalizando..."
              : "Concluir configuração"}
          </Button>
          <p className="text-center text-xs text-gray-400">
            Você pode ajustar suas metas a qualquer momento nas configurações
          </p>
        </div>
      )}
    </div>
  );
}
