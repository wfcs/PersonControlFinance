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
        <Card className="w-full max-w-[420px] border-0 shadow-xl bg-card/95 backdrop-blur-sm">
            <CardHeader className="text-center space-y-2 pb-2">
                <div className="mx-auto w-12 h-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground font-bold text-xl mb-2">
                    V
                </div>
                <CardTitle className="text-2xl font-bold">Criar conta</CardTitle>
                <CardDescription>
                    Comece grátis — conecte suas contas em minutos
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {error && (
                        <div className="rounded-lg bg-destructive/10 text-destructive text-sm px-4 py-2.5 font-medium">
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <Label htmlFor="full_name">Nome completo</Label>
                        <Input
                            id="full_name"
                            placeholder="Seu nome"
                            autoComplete="name"
                            {...register("full_name")}
                        />
                        {errors.full_name && (
                            <p className="text-destructive text-xs">{errors.full_name.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="email">E-mail</Label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="seu@email.com"
                            autoComplete="email"
                            {...register("email")}
                        />
                        {errors.email && (
                            <p className="text-destructive text-xs">{errors.email.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="password">Senha</Label>
                        <div className="relative">
                            <Input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="Mínimo 6 caracteres"
                                autoComplete="new-password"
                                className="pr-10"
                                {...register("password")}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                tabIndex={-1}
                            >
                                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                        </div>
                        {errors.password && (
                            <p className="text-destructive text-xs">{errors.password.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="confirmPassword">Confirme a senha</Label>
                        <Input
                            id="confirmPassword"
                            type={showPassword ? "text" : "password"}
                            placeholder="Repita a senha"
                            autoComplete="new-password"
                            {...register("confirmPassword")}
                        />
                        {errors.confirmPassword && (
                            <p className="text-destructive text-xs">{errors.confirmPassword.message}</p>
                        )}
                    </div>

                    <Button type="submit" className="w-full" disabled={isSubmitting}>
                        {isSubmitting ? (
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : null}
                        Criar conta
                    </Button>
                </form>

                <p className="text-center text-sm text-muted-foreground mt-6">
                    Já tem conta?{" "}
                    <Link
                        href="/login"
                        className="text-primary font-medium hover:underline"
                    >
                        Fazer login
                    </Link>
                </p>
            </CardContent>
        </Card>
    );
}
