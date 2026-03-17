"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { registerApi, fetchMe } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";
import { Eye, EyeOff, Loader2 } from "lucide-react";

const registerSchema = z
    .object({
        full_name: z.string().min(2, "Nome obrigatório"),
        email: z.string().email("E-mail inválido"),
        password: z.string().min(6, "Mínimo de 6 caracteres"),
        confirmPassword: z.string(),
    })
    .refine((d) => d.password === d.confirmPassword, {
        message: "As senhas não coincidem",
        path: ["confirmPassword"],
    });

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const router = useRouter();
    const { setTokens, setUser } = useAuthStore();
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

    const onSubmit = async (values: RegisterForm) => {
        setError(null);
        try {
            const tokens = await registerApi(values.email, values.password, values.full_name);
            setTokens(tokens.access_token, tokens.refresh_token);
            const me = await fetchMe();
            setUser({
                id: me.id,
                email: me.email,
                full_name: me.full_name,
                tenant_id: me.tenant_id,
            });
            router.push("/onboarding");
        } catch {
            setError("Não foi possível criar a conta. Tente outro e-mail.");
        }
    };

    return (
        <Card className="w-full max-w-[480px] border-border/30 shadow-2xl bg-gradient-to-br from-card to-card/80 backdrop-blur-md rounded-2xl animate-fade-in-scale">
            <CardHeader className="text-center space-y-3 pb-3">
                <div className="mx-auto w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center text-primary-foreground font-bold text-2xl shadow-lg">
                    F
                </div>
                <div className="space-y-1">
                    <CardTitle className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                        Criar conta
                    </CardTitle>
                    <CardDescription className="text-sm">
                        Comece grátis — conecte suas contas em minutos
                    </CardDescription>
                </div>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {error && (
                        <div className="rounded-lg border border-destructive/30 bg-gradient-to-r from-destructive/10 to-destructive/5 text-destructive text-sm px-4 py-3 font-medium animate-slide-in-top">
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <Label htmlFor="full_name" className="text-sm font-semibold">Nome completo</Label>
                        <Input
                            id="full_name"
                            placeholder="Seu nome"
                            autoComplete="name"
                            className="h-11 rounded-lg border-border/50 focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                            {...register("full_name")}
                        />
                        {errors.full_name && (
                            <p className="text-destructive text-xs font-medium">{errors.full_name.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="email" className="text-sm font-semibold">E-mail</Label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="seu@email.com"
                            autoComplete="email"
                            className="h-11 rounded-lg border-border/50 focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                            {...register("email")}
                        />
                        {errors.email && (
                            <p className="text-destructive text-xs font-medium">{errors.email.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="password" className="text-sm font-semibold">Senha</Label>
                        <div className="relative">
                            <Input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="Mínimo 6 caracteres"
                                autoComplete="new-password"
                                className="h-11 pr-11 rounded-lg border-border/50 focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                                {...register("password")}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-0 top-1/2 -translate-y-1/2 flex items-center justify-center w-11 text-muted-foreground hover:text-foreground transition-colors"
                                tabIndex={-1}
                            >
                                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                        </div>
                        {errors.password && (
                            <p className="text-destructive text-xs font-medium">{errors.password.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="confirmPassword" className="text-sm font-semibold">Confirme a senha</Label>
                        <Input
                            id="confirmPassword"
                            type={showPassword ? "text" : "password"}
                            placeholder="Repita a senha"
                            autoComplete="new-password"
                            className="h-11 rounded-lg border-border/50 focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                            {...register("confirmPassword")}
                        />
                        {errors.confirmPassword && (
                            <p className="text-destructive text-xs font-medium">{errors.confirmPassword.message}</p>
                        )}
                    </div>

                    <Button 
                        type="submit" 
                        className="w-full h-11 bg-gradient-to-r from-primary to-primary/90 hover:shadow-lg hover:shadow-primary/20 transition-all rounded-lg font-semibold mt-2" 
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                Criando...
                            </>
                        ) : (
                            "Criar conta"
                        )}
                    </Button>
                </form>

                <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-border/30" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-card text-muted-foreground">Já tem conta?</span>
                    </div>
                </div>

                <p className="text-center text-sm">
                    <Link
                        href="/login"
                        className="font-semibold text-primary hover:opacity-80 transition-opacity"
                    >
                        Fazer login →
                    </Link>
                </p>
            </CardContent>
        </Card>
    );
}
