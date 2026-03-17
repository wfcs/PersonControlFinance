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
import { loginApi, fetchMe } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";
import { Eye, EyeOff, Loader2, ArrowRight, AlertCircle } from "lucide-react";

const loginSchema = z.object({
    email: z.string().email("E-mail inválido"),
    password: z.string().min(6, "Mínimo de 6 caracteres"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const router = useRouter();
    const { setTokens, setUser } = useAuthStore();
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

    const onSubmit = async (values: LoginForm) => {
        setError(null);
        try {
            const tokens = await loginApi(values.email, values.password);
            setTokens(tokens.access_token, tokens.refresh_token);
            const me = await fetchMe();
            setUser({
                id: me.id,
                email: me.email,
                full_name: me.full_name,
                tenant_id: me.tenant_id,
            });
            router.push("/dashboard");
        } catch {
            setError("E-mail ou senha incorretos.");
        }
    };

    return (
        <>
            {/* Mobile-only brand (hidden on lg+ where left panel shows) */}
            <div className="flex items-center gap-3 mb-8 lg:hidden">
                <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-primary-foreground font-bold text-lg">
                    F
                </div>
                <span className="text-xl font-semibold tracking-tight">
                    FinControl
                </span>
            </div>

            <div className="space-y-6">
                <div className="space-y-2">
                    <h1 className="text-2xl font-bold tracking-tight">
                        Bem-vindo de volta
                    </h1>
                    <p className="text-muted-foreground text-sm">
                        Entre na sua conta para acessar o dashboard
                    </p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {error && (
                        <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 text-destructive text-sm px-4 py-2.5 font-medium">
                            <AlertCircle className="h-4 w-4 shrink-0" />
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <Label htmlFor="email">E-mail</Label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="seu@email.com"
                            autoComplete="email"
                            autoFocus
                            className="h-11"
                            {...register("email")}
                        />
                        {errors.email && (
                            <p className="text-destructive text-xs">
                                {errors.email.message}
                            </p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <Label htmlFor="password">Senha</Label>
                            <button
                                type="button"
                                className="text-xs text-primary hover:underline"
                            >
                                Esqueceu a senha?
                            </button>
                        </div>
                        <div className="relative">
                            <Input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="••••••"
                                autoComplete="current-password"
                                className="h-11 pr-11"
                                {...register("password")}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 flex items-center justify-center w-11 text-muted-foreground hover:text-foreground transition-colors"
                                tabIndex={-1}
                            >
                                {showPassword ? (
                                    <EyeOff className="h-4 w-4" />
                                ) : (
                                    <Eye className="h-4 w-4" />
                                )}
                            </button>
                        </div>
                        {errors.password && (
                            <p className="text-destructive text-xs">
                                {errors.password.message}
                            </p>
                        )}
                    </div>

                    <Button
                        type="submit"
                        className="w-full h-11"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? (
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : null}
                        Entrar
                        {!isSubmitting && (
                            <ArrowRight className="h-4 w-4 ml-2" />
                        )}
                    </Button>
                </form>

                {/* Divider */}
                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-background px-3 text-muted-foreground">
                            Novo por aqui?
                        </span>
                    </div>
                </div>

                <Link href="/register" className="block">
                    <Button
                        variant="outline"
                        className="w-full h-11"
                        type="button"
                    >
                        Criar conta gratuita
                    </Button>
                </Link>
            </div>
        </>
    );
}
