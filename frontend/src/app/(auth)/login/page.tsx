"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin } from "@/hooks/use-auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = useLogin();

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    login.mutate({ email, password });
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          Bem-vindo de volta
        </h1>
        <p className="text-sm text-gray-500">
          Entre com seus dados para acessar sua conta
        </p>
      </div>

      {login.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {(login.error as { response?: { data?: { detail?: string } } })
            ?.response?.data?.detail ?? "E-mail ou senha inválidos. Tente novamente."}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="email">E-mail</Label>
          <Input
            id="email"
            type="email"
            placeholder="voce@exemplo.com"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Senha</Label>
            <Link
              href="/forgot-password"
              className="text-xs text-blue-600 hover:underline"
            >
              Esqueceu a senha?
            </Link>
          </div>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <Button
          type="submit"
          className="w-full"
          size="lg"
          disabled={login.isPending}
        >
          {login.isPending ? "Entrando..." : "Entrar"}
        </Button>
      </form>

      <p className="text-center text-sm text-gray-500">
        Novo por aqui?{" "}
        <Link
          href="/register"
          className="font-medium text-blue-600 hover:underline"
        >
          Criar conta gratuita
        </Link>
      </p>
    </div>
  );
}
