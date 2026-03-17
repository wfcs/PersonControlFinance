"use client";

import { usePathname } from "next/navigation";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/stores/auth-store";
import { LogOut, User, Settings } from "lucide-react";
import { useRouter } from "next/navigation";

const routeTitles: Record<string, string> = {
    "/dashboard": "Visão Geral",
    "/transactions": "Transações",
    "/accounts": "Contas",
    "/recurring": "Recorrentes",
    "/cash-flow": "Fluxo de Caixa",
    "/invoices": "Faturas",
    "/categories": "Categorias",
    "/goals": "Metas",
    "/projection": "Projeção",
    "/net-worth": "Patrimônio",
    "/reports": "Relatórios",
    "/plans": "Planos",
    "/onboarding": "Configuração Inicial",
    "/admin": "Painel Admin",
};

function getPageTitle(pathname: string): string {
    return routeTitles[pathname] ?? "Visor";
}

export function Header() {
    const pathname = usePathname();
    const router = useRouter();
    const user = useAuthStore((s) => s.user);
    const logout = useAuthStore((s) => s.logout);

    const initials = user?.full_name
        ? user.full_name
            .split(" ")
            .map((w) => w[0])
            .join("")
            .slice(0, 2)
            .toUpperCase()
        : user?.email?.slice(0, 2).toUpperCase() ?? "U";

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

    return (
        <header className="flex items-center justify-between h-16 px-6 border-b bg-card/80 backdrop-blur-sm shrink-0">
            <div>
                <h1 className="text-lg font-semibold">{getPageTitle(pathname)}</h1>
            </div>

            <DropdownMenu>
                {/* @ts-expect-error asChild Radix compatibility */}
                <DropdownMenuTrigger asChild>
                    <button className="flex items-center gap-2 rounded-full hover:opacity-80 transition-opacity focus:outline-none">
                        <Avatar className="h-8 w-8 border border-border">
                            <AvatarFallback className="bg-primary text-primary-foreground text-xs font-medium">
                                {initials}
                            </AvatarFallback>
                        </Avatar>
                    </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                    <div className="px-2 py-1.5 text-sm">
                        <p className="font-medium truncate">{user?.full_name ?? "Usuário"}</p>
                        <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>
                        <User className="mr-2 h-4 w-4" />
                        Perfil
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                        <Settings className="mr-2 h-4 w-4" />
                        Configurações
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
                        <LogOut className="mr-2 h-4 w-4" />
                        Sair
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </header>
    );
}
