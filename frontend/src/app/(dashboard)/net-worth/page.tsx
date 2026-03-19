"use client";

import { formatCurrency } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, TrendingDown, Scale } from "lucide-react";

const MOCK_HISTORY = [
  { month: "Out/25", ativos: 85000, passivos: 32000 },
  { month: "Nov/25", ativos: 88000, passivos: 31000 },
  { month: "Dez/25", ativos: 91000, passivos: 30500 },
  { month: "Jan/26", ativos: 94500, passivos: 29000 },
  { month: "Fev/26", ativos: 97000, passivos: 28000 },
  { month: "Mar/26", ativos: 102000, passivos: 27500 },
].map((d) => ({ ...d, patrimonio: d.ativos - d.passivos }));

const ASSET_BREAKDOWN = [
  { name: "Conta Corrente", value: 8500, category: "Liquidez" },
  { name: "Poupança", value: 15000, category: "Liquidez" },
  { name: "Investimentos", value: 55000, category: "Investimentos" },
  { name: "Imóvel", value: 23500, category: "Imóveis" },
];

const LIABILITY_BREAKDOWN = [
  { name: "Cartão de Crédito", value: 8200, category: "Curto prazo" },
  { name: "Financiamento", value: 19300, category: "Longo prazo" },
];

const latest = MOCK_HISTORY[MOCK_HISTORY.length - 1];
const previous = MOCK_HISTORY[MOCK_HISTORY.length - 2];
const netWorthChange = latest.patrimonio - previous.patrimonio;
const netWorthChangePct = ((netWorthChange / previous.patrimonio) * 100).toFixed(1);

export default function NetWorthPage() {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Patrimônio Líquido</h1>
        <p className="text-sm text-gray-500">Visão geral dos seus ativos e passivos</p>
      </div>

      {/* Top summary */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="border-green-200 bg-green-50">
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-green-700">
              <TrendingUp className="h-4 w-4" />
              Total de Ativos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-700">{formatCurrency(latest.ativos)}</p>
          </CardContent>
        </Card>
        <Card className="border-red-200 bg-red-50">
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-red-700">
              <TrendingDown className="h-4 w-4" />
              Total de Passivos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-700">{formatCurrency(latest.passivos)}</p>
          </CardContent>
        </Card>
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-blue-700">
              <Scale className="h-4 w-4" />
              Patrimônio Líquido
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-blue-700">{formatCurrency(latest.patrimonio)}</p>
            <p className={`text-xs font-medium ${netWorthChange >= 0 ? "text-green-600" : "text-red-600"}`}>
              {netWorthChange >= 0 ? "+" : ""}{formatCurrency(netWorthChange)} ({netWorthChangePct}%) vs mês anterior
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Area chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Evolução do Patrimônio (6 meses)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={MOCK_HISTORY} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
              <defs>
                <linearGradient id="colorAtivos" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorPassivos" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorPatrimonio" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Area type="monotone" dataKey="ativos" stroke="#22c55e" fill="url(#colorAtivos)" strokeWidth={2} name="Ativos" />
              <Area type="monotone" dataKey="passivos" stroke="#ef4444" fill="url(#colorPassivos)" strokeWidth={2} name="Passivos" />
              <Area type="monotone" dataKey="patrimonio" stroke="#3b82f6" fill="url(#colorPatrimonio)" strokeWidth={2.5} name="Patrimônio" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Breakdown */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base text-green-700">Ativos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {ASSET_BREAKDOWN.map((item) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{item.name}</p>
                    <p className="text-xs text-gray-400">{item.category}</p>
                  </div>
                  <p className="text-sm font-semibold text-green-700">{formatCurrency(item.value)}</p>
                </div>
              ))}
              <div className="border-t pt-2 flex justify-between">
                <p className="text-sm font-bold">Total</p>
                <p className="text-sm font-bold text-green-700">{formatCurrency(latest.ativos)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base text-red-700">Passivos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {LIABILITY_BREAKDOWN.map((item) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{item.name}</p>
                    <p className="text-xs text-gray-400">{item.category}</p>
                  </div>
                  <p className="text-sm font-semibold text-red-700">{formatCurrency(item.value)}</p>
                </div>
              ))}
              <div className="border-t pt-2 flex justify-between">
                <p className="text-sm font-bold">Total</p>
                <p className="text-sm font-bold text-red-700">{formatCurrency(latest.passivos)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
