"use client";

import { formatCurrency, formatDate } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreditCard } from "lucide-react";

interface Invoice {
  id: string;
  cardName: string;
  bank: string;
  limit: number;
  currentTotal: number;
  dueDate: string;
  closingDate: string;
  status: "open" | "closed" | "overdue";
  lastDigits: string;
}

const MOCK_INVOICES: Invoice[] = [
  {
    id: "1",
    cardName: "Nubank Mastercard",
    bank: "Nubank",
    limit: 8000,
    currentTotal: 2345.67,
    dueDate: "2026-04-10",
    closingDate: "2026-04-03",
    status: "open",
    lastDigits: "4321",
  },
  {
    id: "2",
    cardName: "Itaú Visa Gold",
    bank: "Itaú",
    limit: 12000,
    currentTotal: 5890.0,
    dueDate: "2026-04-15",
    closingDate: "2026-04-08",
    status: "open",
    lastDigits: "9876",
  },
  {
    id: "3",
    cardName: "Bradesco Elo",
    bank: "Bradesco",
    limit: 5000,
    currentTotal: 1200.5,
    dueDate: "2026-03-20",
    closingDate: "2026-03-13",
    status: "overdue",
    lastDigits: "5555",
  },
  {
    id: "4",
    cardName: "Inter Mastercard",
    bank: "Inter",
    limit: 6000,
    currentTotal: 0,
    dueDate: "2026-04-05",
    closingDate: "2026-03-28",
    status: "closed",
    lastDigits: "1234",
  },
];

const STATUS_LABELS: Record<string, string> = {
  open: "Em aberto",
  closed: "Fechada",
  overdue: "Vencida",
};

const STATUS_CLASSES: Record<string, string> = {
  open: "bg-blue-100 text-blue-700",
  closed: "bg-gray-100 text-gray-700",
  overdue: "bg-red-100 text-red-700",
};

const CARD_COLORS = [
  "from-purple-600 to-purple-800",
  "from-blue-600 to-blue-800",
  "from-red-600 to-red-800",
  "from-orange-500 to-orange-700",
];

export default function InvoicesPage() {
  const totalOpen = MOCK_INVOICES.filter((i) => i.status === "open" || i.status === "overdue")
    .reduce((acc, i) => acc + i.currentTotal, 0);

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Faturas</h1>
        <p className="text-sm text-gray-500">Acompanhe suas faturas de cartão de crédito</p>
      </div>

      {/* Summary */}
      <div className="rounded-lg border bg-blue-50 p-4">
        <p className="text-sm text-blue-600">Total em faturas abertas</p>
        <p className="text-3xl font-bold text-blue-700">{formatCurrency(totalOpen)}</p>
      </div>

      {MOCK_INVOICES.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-20 text-center">
          <CreditCard className="mb-4 h-12 w-12 text-gray-300" />
          <h3 className="text-base font-semibold text-gray-700">Nenhuma fatura encontrada</h3>
          <p className="text-sm text-gray-400">As faturas dos seus cartões aparecerão aqui</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-2">
          {MOCK_INVOICES.map((invoice, idx) => {
            const usedPercent = Math.round((invoice.currentTotal / invoice.limit) * 100);
            return (
              <Card key={invoice.id} className="overflow-hidden">
                {/* Card visual */}
                <div className={`bg-gradient-to-br ${CARD_COLORS[idx % CARD_COLORS.length]} p-5 text-white`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium opacity-75">{invoice.bank}</p>
                      <p className="mt-1 text-lg font-bold">{invoice.cardName}</p>
                    </div>
                    <CreditCard className="h-8 w-8 opacity-60" />
                  </div>
                  <p className="mt-4 font-mono text-sm tracking-widest opacity-75">
                    **** **** **** {invoice.lastDigits}
                  </p>
                </div>

                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-xs text-gray-500">Fatura atual</p>
                      <p className="text-xl font-bold">{formatCurrency(invoice.currentTotal)}</p>
                    </div>
                    <Badge className={`text-xs ${STATUS_CLASSES[invoice.status]}`} variant="secondary">
                      {STATUS_LABELS[invoice.status]}
                    </Badge>
                  </div>

                  {/* Usage bar */}
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Limite utilizado</span>
                      <span>{usedPercent}% de {formatCurrency(invoice.limit)}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-100">
                      <div
                        className={`h-2 rounded-full transition-all ${usedPercent > 80 ? "bg-red-500" : usedPercent > 50 ? "bg-orange-400" : "bg-green-500"}`}
                        style={{ width: `${Math.min(usedPercent, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Fechamento: {formatDate(invoice.closingDate)}</span>
                    <span>Vencimento: {formatDate(invoice.dueDate)}</span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
