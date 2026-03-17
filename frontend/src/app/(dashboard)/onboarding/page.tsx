"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/stores/auth-store";
import { useCreateAccount } from "@/hooks/use-accounts";
import {
    ArrowRight,
    ArrowLeft,
    Loader2,
    CheckCircle2,
    Wallet,
    TrendingUp,
    ShieldCheck,
    Target,
} from "lucide-react";

const STEPS = [
    { title: "Boas-vindas", subtitle: "Vamos configurar sua conta" },
    { title: "Primeira conta", subtitle: "Adicione sua conta bancária principal" },
    { title: "Seus objetivos", subtitle: "O que você deseja alcançar?" },
    { title: "Tudo pronto!", subtitle: "Sua configuração está completa" },
];

const GOALS = [
    {
        id: "control",
        label: "Controle de gastos",
        desc: "Entender para onde vai meu dinheiro",
        icon: Wallet,
    },
    {
        id: "invest",
        label: "Investir mais",
        desc: "Encontrar oportunidades de investimento",
        icon: TrendingUp,
    },
    {
        id: "debts",
        label: "Sair das dívidas",
        desc: "Eliminar dívidas e financiamentos",
        icon: ShieldCheck,
    },
    {
        id: "patrimony",
        label: "Construir patrimônio",
        desc: "Acompanhar e crescer meu patrimônio",
        icon: Target,
    },
];

export default function OnboardingPage() {
    const router = useRouter();
    const user = useAuthStore((s) => s.user);
    const createAccount = useCreateAccount();

    const [step, setStep] = useState(0);
    const [accountName, setAccountName] = useState("");
    const [institutionName, setInstitutionName] = useState("");
    const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

    const firstName = user?.full_name?.split(" ")[0] ?? "usuário";

    const toggleGoal = (id: string) => {
        setSelectedGoals((prev) =>
            prev.includes(id) ? prev.filter((g) => g !== id) : [...prev, id]
        );
    };

    const handleCreateAccount = async () => {
        if (!accountName || !institutionName) return;
        await createAccount.mutateAsync({
            name: accountName,
            institution_name: institutionName,
            type: "checking",
            balance: 0,
        });
        setStep(2);
    };

    const progress = ((step + 1) / STEPS.length) * 100;

    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] px-4 py-8">
            {/* Progress bar */}
            <div className="w-full max-w-lg mb-8">
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                        className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                    Passo {step + 1} de {STEPS.length}
                </p>
            </div>

            <div className="w-full max-w-lg bg-card rounded-2xl border p-8 shadow-sm">
                <h2 className="text-xl font-bold mb-1">{STEPS[step].title}</h2>
                <p className="text-sm text-muted-foreground mb-6">
                    {STEPS[step].subtitle}
                </p>

                {/* Step 0: Welcome */}
                {step === 0 && (
                    <div className="space-y-4">
                        <p className="text-base">
                            Olá, <span className="font-semibold">{firstName}</span>! 👋
                        </p>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                            Em poucos passos, vamos configurar sua conta para que
                            você tenha controle total das suas finanças. Vamos lá?
                        </p>
                        <Button
                            onClick={() => setStep(1)}
                            className="w-full h-11 mt-4"
                        >
                            Começar
                            <ArrowRight className="h-4 w-4 ml-2" />
                        </Button>
                    </div>
                )}

                {/* Step 1: First Account */}
                {step === 1 && (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="accountName">Nome da conta</Label>
                            <Input
                                id="accountName"
                                placeholder="Ex: Conta corrente Nubank"
                                value={accountName}
                                onChange={(e) => setAccountName(e.target.value)}
                                className="h-11"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="institution">Instituição</Label>
                            <Input
                                id="institution"
                                placeholder="Ex: Nubank, Itaú, Bradesco"
                                value={institutionName}
                                onChange={(e) =>
                                    setInstitutionName(e.target.value)
                                }
                                className="h-11"
                            />
                        </div>
                        <div className="flex gap-3 mt-4">
                            <Button
                                variant="outline"
                                onClick={() => setStep(0)}
                                className="h-11"
                            >
                                <ArrowLeft className="h-4 w-4 mr-2" />
                                Voltar
                            </Button>
                            <Button
                                onClick={handleCreateAccount}
                                disabled={
                                    !accountName ||
                                    !institutionName ||
                                    createAccount.isPending
                                }
                                className="flex-1 h-11"
                            >
                                {createAccount.isPending ? (
                                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                ) : null}
                                Adicionar conta
                                <ArrowRight className="h-4 w-4 ml-2" />
                            </Button>
                        </div>
                    </div>
                )}

                {/* Step 2: Goals */}
                {step === 2 && (
                    <div className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {GOALS.map((goal) => {
                                const Icon = goal.icon;
                                const selected = selectedGoals.includes(
                                    goal.id
                                );
                                return (
                                    <button
                                        key={goal.id}
                                        onClick={() => toggleGoal(goal.id)}
                                        className={`text-left p-4 rounded-xl border-2 transition-all ${
                                            selected
                                                ? "border-primary bg-primary/5"
                                                : "border-border hover:border-primary/40"
                                        }`}
                                    >
                                        <Icon
                                            className={`h-5 w-5 mb-2 ${
                                                selected
                                                    ? "text-primary"
                                                    : "text-muted-foreground"
                                            }`}
                                        />
                                        <p className="font-medium text-sm">
                                            {goal.label}
                                        </p>
                                        <p className="text-xs text-muted-foreground mt-0.5">
                                            {goal.desc}
                                        </p>
                                    </button>
                                );
                            })}
                        </div>
                        <div className="flex gap-3 mt-4">
                            <Button
                                variant="outline"
                                onClick={() => setStep(1)}
                                className="h-11"
                            >
                                <ArrowLeft className="h-4 w-4 mr-2" />
                                Voltar
                            </Button>
                            <Button
                                onClick={() => setStep(3)}
                                className="flex-1 h-11"
                            >
                                Continuar
                                <ArrowRight className="h-4 w-4 ml-2" />
                            </Button>
                        </div>
                    </div>
                )}

                {/* Step 3: Done */}
                {step === 3 && (
                    <div className="text-center space-y-4">
                        <CheckCircle2 className="h-16 w-16 text-emerald-500 mx-auto" />
                        <p className="text-base font-medium">
                            Tudo configurado, {firstName}!
                        </p>
                        <p className="text-sm text-muted-foreground">
                            Sua conta e objetivos foram registrados. Agora você
                            pode explorar o dashboard e começar a controlar suas
                            finanças.
                        </p>
                        <Button
                            onClick={() => router.push("/dashboard")}
                            className="w-full h-11 mt-4"
                        >
                            Ir para o Dashboard
                            <ArrowRight className="h-4 w-4 ml-2" />
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
