"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Check, Zap, Crown, Sparkles } from "lucide-react";

type Billing = "mensal" | "anual";

const PLANS = [
  {
    id: "free",
    name: "Free",
    icon: Zap,
    description: "Para quem está começando",
    monthlyPrice: 0,
    annualPrice: 0,
    color: "border-gray-200",
    badge: null,
    current: true,
    features: [
      "Até 2 contas",
      "50 transações/mês",
      "Categorias básicas",
      "Relatório mensal",
      "Suporte por e-mail",
    ],
    missing: [
      "Metas ilimitadas",
      "Projeção financeira",
      "Fluxo de caixa avançado",
      "Exportação de dados",
      "Suporte prioritário",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    icon: Crown,
    description: "Para uso pessoal avançado",
    monthlyPrice: 29.9,
    annualPrice: 24.9,
    color: "border-blue-500 ring-2 ring-blue-500",
    badge: "Mais popular",
    current: false,
    features: [
      "Contas ilimitadas",
      "Transações ilimitadas",
      "Categorias personalizadas",
      "Relatórios avançados",
      "Metas ilimitadas",
      "Projeção financeira",
      "Fluxo de caixa",
      "Exportação CSV/PDF",
      "Suporte prioritário",
    ],
    missing: [
      "Multi-usuário",
      "API de integração",
    ],
  },
  {
    id: "premium",
    name: "Premium",
    icon: Sparkles,
    description: "Para famílias e times",
    monthlyPrice: 59.9,
    annualPrice: 49.9,
    color: "border-purple-400",
    badge: "Em breve",
    current: false,
    features: [
      "Tudo do Pro",
      "Até 5 usuários",
      "API de integração",
      "Importação bancária automática",
      "Dashboard multi-usuário",
      "Relatórios personalizados",
      "Gerente de conta dedicado",
      "SLA de suporte 4h",
    ],
    missing: [],
  },
];

export default function PlansPage() {
  const [billing, setBilling] = useState<Billing>("mensal");

  return (
    <div className="space-y-8 p-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight">Planos e Preços</h1>
        <p className="mt-1 text-sm text-gray-500">Escolha o plano ideal para você</p>
      </div>

      {/* Billing toggle */}
      <div className="flex justify-center">
        <div className="flex items-center rounded-full border bg-white p-1 shadow-sm">
          <button
            onClick={() => setBilling("mensal")}
            className={`rounded-full px-5 py-2 text-sm font-medium transition-colors ${
              billing === "mensal" ? "bg-blue-600 text-white shadow" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Mensal
          </button>
          <button
            onClick={() => setBilling("anual")}
            className={`relative rounded-full px-5 py-2 text-sm font-medium transition-colors ${
              billing === "anual" ? "bg-blue-600 text-white shadow" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Anual
            <span className="absolute -top-2.5 -right-2 rounded-full bg-green-500 px-1.5 py-0.5 text-[10px] font-bold text-white leading-none">
              -17%
            </span>
          </button>
        </div>
      </div>

      {/* Plan cards */}
      <div className="grid gap-6 sm:grid-cols-3">
        {PLANS.map((plan) => {
          const price = billing === "anual" ? plan.annualPrice : plan.monthlyPrice;
          const Icon = plan.icon;

          return (
            <Card key={plan.id} className={`relative flex flex-col ${plan.color}`}>
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge
                    className={`px-3 py-0.5 text-xs ${
                      plan.badge === "Mais popular"
                        ? "bg-blue-600 text-white"
                        : "bg-purple-100 text-purple-700"
                    }`}
                  >
                    {plan.badge}
                  </Badge>
                </div>
              )}
              <CardHeader className="pb-2 pt-6">
                <div className="flex items-center gap-2">
                  <div className={`flex h-9 w-9 items-center justify-center rounded-full ${
                    plan.id === "free" ? "bg-gray-100" : plan.id === "pro" ? "bg-blue-100" : "bg-purple-100"
                  }`}>
                    <Icon className={`h-5 w-5 ${
                      plan.id === "free" ? "text-gray-600" : plan.id === "pro" ? "text-blue-600" : "text-purple-600"
                    }`} />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{plan.name}</CardTitle>
                    <p className="text-xs text-gray-400">{plan.description}</p>
                  </div>
                </div>
                <div className="mt-3">
                  {price === 0 ? (
                    <p className="text-3xl font-bold">Grátis</p>
                  ) : (
                    <div className="flex items-end gap-1">
                      <p className="text-3xl font-bold">
                        {price.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                      </p>
                      <p className="mb-1 text-sm text-gray-400">/mês</p>
                    </div>
                  )}
                  {billing === "anual" && price > 0 && (
                    <p className="text-xs text-green-600">
                      Cobrado anualmente · economia de R${((plan.monthlyPrice - plan.annualPrice) * 12).toFixed(0)}/ano
                    </p>
                  )}
                </div>
              </CardHeader>
              <CardContent className="flex flex-1 flex-col gap-4">
                <ul className="space-y-2">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm">
                      <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-500" />
                      <span>{f}</span>
                    </li>
                  ))}
                  {plan.missing.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-gray-300 line-through">
                      <Check className="mt-0.5 h-4 w-4 flex-shrink-0 opacity-30" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-auto pt-2">
                  {plan.current ? (
                    <Button variant="outline" className="w-full" disabled>
                      Plano atual
                    </Button>
                  ) : plan.badge === "Em breve" ? (
                    <Button variant="outline" className="w-full" disabled>
                      Em breve
                    </Button>
                  ) : (
                    <Button
                      className={`w-full ${plan.id === "pro" ? "bg-blue-600 hover:bg-blue-700" : ""}`}
                    >
                      Fazer upgrade
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="text-center text-xs text-gray-400">
        Todos os planos incluem SSL, backups diários e conformidade com LGPD.
        Cancele a qualquer momento sem multa.
      </div>
    </div>
  );
}
