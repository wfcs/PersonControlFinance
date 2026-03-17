import { Landmark, ShieldCheck, TrendingUp, Zap } from "lucide-react";

const features = [
    {
        icon: Landmark,
        title: "Open Finance",
        desc: "Conexão direta com seus bancos via API oficial.",
    },
    {
        icon: TrendingUp,
        title: "Projeções inteligentes",
        desc: "IA que antecipa seu fluxo de caixa e despesas.",
    },
    {
        icon: ShieldCheck,
        title: "Segurança de ponta",
        desc: "Criptografia de dados e autenticação multi-fator.",
    },
    {
        icon: Zap,
        title: "Sincronização automática",
        desc: "Transações atualizadas em tempo real, sem esforço.",
    },
];

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen flex">
            {/* Left brand panel — visible on lg+ */}
            <div className="hidden lg:flex lg:w-[480px] xl:w-[540px] flex-col justify-between bg-[oklch(0.16_0.03_260)] text-white p-10 relative overflow-hidden">
                {/* Decorative orbs */}
                <div className="absolute -top-24 -left-24 w-72 h-72 rounded-full bg-[oklch(0.50_0.16_260)] opacity-15 blur-3xl" />
                <div className="absolute bottom-10 right-0 w-56 h-56 rounded-full bg-[oklch(0.60_0.17_160)] opacity-10 blur-3xl" />

                <div className="relative z-10">
                    {/* Brand */}
                    <div className="flex items-center gap-3 mb-16">
                        <div className="w-10 h-10 rounded-xl bg-[oklch(0.50_0.16_260)] flex items-center justify-center text-white font-bold text-lg">
                            F
                        </div>
                        <span className="text-xl font-semibold tracking-tight">
                            FinControl
                        </span>
                    </div>

                    {/* Features */}
                    <div className="space-y-6">
                        {features.map((f) => {
                            const Icon = f.icon;
                            return (
                                <div
                                    key={f.title}
                                    className="flex items-start gap-4 p-4 rounded-xl bg-white/[0.04] border border-white/[0.06]"
                                >
                                    <div className="w-9 h-9 rounded-lg bg-[oklch(0.50_0.16_260)]/20 flex items-center justify-center shrink-0">
                                        <Icon className="h-[18px] w-[18px] text-[oklch(0.75_0.12_260)]" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-sm text-white/90">
                                            {f.title}
                                        </p>
                                        <p className="text-sm text-white/50 mt-0.5 leading-relaxed">
                                            {f.desc}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Footer */}
                <p className="relative z-10 text-xs text-white/30">
                    © {new Date().getFullYear()} FinControl. Todos os direitos
                    reservados.
                </p>
            </div>

            {/* Right form panel */}
            <div className="flex-1 flex items-center justify-center bg-background px-6 py-12">
                <div className="w-full max-w-[420px]">{children}</div>
            </div>
        </div>
    );
}
