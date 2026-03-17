"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Sheet,
    SheetContent,
    SheetTrigger,
    SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
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
    Menu,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

const navItems = [
    { label: "Visão Geral", href: "/dashboard", icon: LayoutDashboard },
    { label: "Transações", href: "/transactions", icon: ArrowLeftRight },
    { label: "Contas", href: "/accounts", icon: Wallet },
    { label: "Recorrentes", href: "/recurring", icon: Repeat, disabled: true },
    { label: "Fluxo de Caixa", href: "/cash-flow", icon: BarChart3, disabled: true },
    { label: "Faturas", href: "/invoices", icon: CreditCard, disabled: true },
    { label: "Categorias", href: "/categories", icon: Tags, disabled: true },
    { label: "Metas", href: "/goals", icon: Target, disabled: true },
    { label: "Projeção", href: "/projection", icon: TrendingUp, disabled: true },
    { label: "Patrimônio", href: "/net-worth", icon: PieChart, disabled: true },
    { label: "Relatórios", href: "/reports", icon: FileText, disabled: true },
    { label: "Planos", href: "/plans", icon: Gem, disabled: true },
];

export function MobileNav() {
    const pathname = usePathname();
    const [open, setOpen] = useState(false);

    return (
        <Sheet open={open} onOpenChange={setOpen}>
            {/* @ts-expect-error asChild Radix compatibility */}
            <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden">
                    <Menu className="h-5 w-5" />
                </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[260px] bg-sidebar text-sidebar-foreground p-0">
                <SheetTitle className="sr-only">Navegação</SheetTitle>
                <div className="flex items-center gap-2.5 px-4 h-16 border-b border-sidebar-border">
                    <div className="w-8 h-8 rounded-lg bg-sidebar-primary flex items-center justify-center text-sidebar-primary-foreground font-bold text-sm">
                        V
                    </div>
                    <span className="text-lg font-semibold tracking-tight">Visor</span>
                </div>
                <nav className="py-3 px-2 space-y-0.5">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href;
                        const Icon = item.icon;
                        return (
                            <Link
                                key={item.href}
                                href={item.disabled ? "#" : item.href}
                                onClick={() => !item.disabled && setOpen(false)}
                                className={cn(
                                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                                    isActive
                                        ? "bg-sidebar-accent text-sidebar-primary"
                                        : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground",
                                    item.disabled && "opacity-40 pointer-events-none"
                                )}
                            >
                                <Icon className="h-[18px] w-[18px]" />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </SheetContent>
        </Sheet>
    );
}
