"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    ArrowLeftRight,
    Wallet,
    Repeat,
    BarChart3,
    CreditCard,
    Tags,
    Target,
    TrendingUp,
    PieChart,
    FileText,
    Gem,
    ShieldCheck,
    ChevronLeft,
    ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

const navItems = [
    { label: "Visão Geral", href: "/dashboard", icon: LayoutDashboard },
    { label: "Transações", href: "/transactions", icon: ArrowLeftRight },
    { label: "Contas", href: "/accounts", icon: Wallet },
    { label: "Recorrentes", href: "/recurring", icon: Repeat },
    { label: "Fluxo de Caixa", href: "/cash-flow", icon: BarChart3 },
    { label: "Faturas", href: "/invoices", icon: CreditCard },
    { label: "Categorias", href: "/categories", icon: Tags },
    { label: "Metas", href: "/goals", icon: Target },
    { label: "Projeção", href: "/projection", icon: TrendingUp },
    { label: "Patrimônio", href: "/net-worth", icon: PieChart },
    { label: "Relatórios", href: "/reports", icon: FileText },
    { label: "Planos", href: "/plans", icon: Gem },
    { label: "Admin", href: "/admin", icon: ShieldCheck },
];

export function Sidebar() {
    const pathname = usePathname();
    const [collapsed, setCollapsed] = useState(false);

    return (
        <aside
            className={cn(
                "hidden md:flex flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border transition-all duration-300 ease-in-out",
                collapsed ? "w-[68px]" : "w-[240px]"
            )}
        >
            {/* Logo */}
            <div className="flex items-center gap-2.5 px-4 h-16 border-b border-sidebar-border shrink-0">
                <div className="w-8 h-8 rounded-lg bg-sidebar-primary flex items-center justify-center text-sidebar-primary-foreground font-bold text-sm shrink-0">
                    V
                </div>
                {!collapsed && (
                    <span className="text-lg font-semibold tracking-tight text-sidebar-foreground">
                        Visor
                    </span>
                )}
            </div>

            {/* Nav */}
            <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
                {navItems.map((item) => {
                    const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.href}
                            href={item.disabled ? "#" : item.href}
                            aria-disabled={item.disabled}
                            title={collapsed ? item.label : undefined}
                            className={cn(
                                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-sidebar-accent text-sidebar-primary"
                                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground",
                                item.disabled && "opacity-40 pointer-events-none cursor-default",
                                collapsed && "justify-center px-2"
                            )}
                        >
                            <Icon className="h-[18px] w-[18px] shrink-0" />
                            {!collapsed && <span>{item.label}</span>}
                        </Link>
                    );
                })}
            </nav>

            {/* Collapse toggle */}
            <button
                onClick={() => setCollapsed(!collapsed)}
                className="flex items-center justify-center h-10 border-t border-sidebar-border text-sidebar-foreground/50 hover:text-sidebar-foreground transition-colors"
            >
                {collapsed ? (
                    <ChevronRight className="h-4 w-4" />
                ) : (
                    <ChevronLeft className="h-4 w-4" />
                )}
            </button>
        </aside>
    );
}
