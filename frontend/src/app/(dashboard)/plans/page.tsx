"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";

export default function PlansPage() {
    const plans = [
        {
            id: "free",
            name: "Básico",
            description: "Para começar",
            price: 0,
            features: [
                "Até 2 contas",
                "Rastreamento de gastos",
                "Categorias padrão",
                "Relatórios básicos",
                "Suporte por email",
            ],
            annual_price: null,
            current: false,
        },
        {
            id: "pro",
            name: "Profissional",
            description: "Mais poder e controle",
            price: 29,
            features: [
                "Contas ilimitadas",
                "Rastreamento avançado",
                "Categorias personalizadas",
                "Orçamento e metas",
                "Detecção de gastos recorrentes",
                "Análise preditiva",
                "Integração Open Finance",
                "Suporte prioritário",
            ],
            annual_price: 290,
            current: true,
        },
        {
            id: "premium",
            name: "Premium",
            description: "Máxima inteligência",
            price: 59,
            features: [
                "Tudo do Profissional",
                "IA para otimização de gastos",
                "Análise de patrimônio",
                "Projeções financeiras 12M",
                "Relatórios customizados",
                "Integração com Stripe/Pluggy",
                "API para automações",
                "Suporte 24/7 e consultor financeiro",
            ],
            annual_price: 590,
            current: false,
        },
    ];

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Planos e Assinatura</h1>
                <p className="text-muted-foreground text-sm mt-1">
                    Escolha o melhor plano para suas necessidades financeiras
                </p>
            </div>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4 bg-muted p-4 rounded-lg mx-auto">
                <span className="text-sm">Mensal</span>
                <div className="relative inline-flex h-8 w-14 items-center rounded-full bg-secondary">
                    <input type="checkbox" className="sr-only" defaultChecked={false} />
                    <span className="inline-block h-6 w-6 translate-x-1 transform rounded-full bg-white transition" />
                </div>
                <span className="text-sm">Anual (economize 17%)</span>
            </div>

            {/* Plans Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {plans.map((plan) => (
                    <Card
                        key={plan.id}
                        className={`relative transition-all ${
                            plan.current ? "ring-2 ring-primary shadow-lg" : "hover:shadow-md"
                        }`}
                    >
                        {/* Current Plan Badge */}
                        {plan.current && (
                            <Badge className="absolute top-4 right-4 bg-primary">Seu plano atual</Badge>
                        )}

                        <CardHeader>
                            <CardTitle className="text-2xl">{plan.name}</CardTitle>
                            <p className="text-sm text-muted-foreground mt-1">{plan.description}</p>

                            {/* Price */}
                            <div className="mt-4">
                                <span className="text-4xl font-bold">R$ {plan.price}</span>
                                <span className="text-muted-foreground">/mês</span>
                                {plan.annual_price && (
                                    <p className="text-xs text-muted-foreground mt-1">
                                        ou R$ {plan.annual_price}/ano
                                    </p>
                                )}
                            </div>
                        </CardHeader>

                        <CardContent className="space-y-4">
                            {/* CTA Button */}
                            <Button className="w-full" variant={plan.current ? "outline" : "default"}>
                                {plan.current ? "Gerenciar assinatura" : "Fazer upgrade"}
                            </Button>

                            {/* Features List */}
                            <div className="space-y-3 pt-4 border-t">
                                {plan.features.map((feature, idx) => (
                                    <div key={idx} className="flex items-start gap-3">
                                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                                        <span className="text-sm">{feature}</span>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* FAQ Section */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Perguntas Frequentes</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Posso mudar de plano?</h4>
                        <p className="text-sm text-muted-foreground">
                            Sim! Você pode fazer upgrade ou downgrade a qualquer momento. As mudanças entram em vigor no próximo ciclo de faturamento.
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Há período de teste?</h4>
                        <p className="text-sm text-muted-foreground">
                            Sim, os planos Pro e Premium têm 7 dias de teste gratuito. Nenhum cartão é necessário.
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Posso cancelar a qualquer momento?</h4>
                        <p className="text-sm text-muted-foreground">
                            Claro! Seu acesso termina ao final do período de faturamento. Sem cobranças surpresa ou taxas de cancelamento.
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">O plano inclui suporte?</h4>
                        <p className="text-sm text-muted-foreground">
                            Todos os planos incluem suporte. O Profissional tem suporte prioritário por email e o Premium tem acesso 24/7 mais suporte dedicado.
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* Current Subscription Card */}
            <Card className="bg-primary/5 border-primary/20">
                <CardHeader>
                    <CardTitle className="text-lg">Sua Assinatura Atual</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-xs text-muted-foreground">Plano</p>
                            <p className="font-semibold">Profissional</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Ciclo de faturamento</p>
                            <p className="font-semibold">Mensal</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Próxima cobrança</p>
                            <p className="font-semibold">15 de Fevereiro, 2025</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Valor</p>
                            <p className="font-semibold">R$ 29,00/mês</p>
                        </div>
                    </div>

                    <div className="flex gap-2 pt-2">
                        <Button variant="outline" className="flex-1">
                            Atualizar Pagamento
                        </Button>
                        <Button variant="ghost" className="flex-1 text-destructive hover:text-destructive">
                            Cancelar Assinatura
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
