"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRegister } from "@/hooks/use-auth";

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantName, setTenantName] = useState("");

  const register = useRegister();

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    register.mutate({
      full_name: fullName,
      email,
      password,
      tenant_name: tenantName,
    });
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          Criar conta
        </h1>
        <p className="text-sm text-gray-500">
          Comece a controlar suas finanças gratuitamente
        </p>
      </div>

      {register.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {(register.error as { response?: { data?: { detail?: string } } })
            ?.response?.data?.detail ?? "Ocorreu um erro. Verifique os dados e tente novamente."}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="full_name">Nome completo</Label>
          <Input
            id="full_name"
            type="text"
            placeholder="Seu nome"
            autoComplete="name"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
        </div>

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
          <Label htmlFor="password">Senha</Label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="tenant_name">Nome da empresa</Label>
          <Input
            id="tenant_name"
            type="text"
            placeholder="Minha Empresa"
            required
            value={tenantName}
            onChange={(e) => setTenantName(e.target.value)}
          />
        </div>

        <Button
          type="submit"
          className="w-full"
          size="lg"
          disabled={register.isPending}
        >
          {register.isPending ? "Criando conta..." : "Criar conta"}
        </Button>
      </form>

      <p className="text-center text-sm text-gray-500">
        Já tem uma conta?{" "}
        <Link
          href="/login"
          className="font-medium text-blue-600 hover:underline"
        >
          Entrar
        </Link>
      </p>
    </div>
  );
}
