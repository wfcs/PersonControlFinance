"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ArrowLeftRight,
  Wallet,
  Tag,
  RefreshCw,
  TrendingUp,
  CreditCard,
  Target,
  LineChart,
  Building,
  BarChart3,
  Crown,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { useLogout } from "@/hooks";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Visão Geral", href: "/dashboard", icon: LayoutDashboard },
  { label: "Transações", href: "/transactions", icon: ArrowLeftRight },
  { label: "Contas", href: "/accounts", icon: Wallet },
  { label: "Categorias", href: "/categories", icon: Tag },
  { label: "Recorrentes", href: "/recurring", icon: RefreshCw },
  { label: "Fluxo de Caixa", href: "/cash-flow", icon: TrendingUp },
  { label: "Faturas", href: "/invoices", icon: CreditCard },
  { label: "Metas", href: "/goals", icon: Target },
  { label: "Projeção", href: "/projection", icon: LineChart },
  { label: "Patrimônio", href: "/net-worth", icon: Building },
  { label: "Relatórios", href: "/reports", icon: BarChart3 },
  { label: "Planos", href: "/plans", icon: Crown },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();

  return (
    <aside className="hidden md:flex flex-col w-60 min-h-screen bg-gray-900 text-white shrink-0">
      {/* Brand */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center font-bold text-sm">
          FC
        </div>
        <span className="text-lg font-semibold tracking-tight">FinControl</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                isActive
                  ? "bg-white/10 font-medium text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              )}
            >
              <Icon size={16} className="shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User / Logout */}
      <div className="border-t border-white/10 px-4 py-4">
        <div className="mb-3">
          <p className="text-sm font-medium text-white truncate">
            {user?.full_name ?? "Usuário"}
          </p>
          <p className="text-xs text-gray-400 truncate">{user?.email ?? ""}</p>
        </div>
        <button
          onClick={() => logout()}
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-white transition-colors"
        >
          <LogOut size={14} />
          Sair
        </button>
      </div>
    </aside>
  );
}
