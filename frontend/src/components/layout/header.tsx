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
        <header className="flex items-center justify-between h-16 px-6 border-b bg-gradient-to-r from-card/80 to-card/40 backdrop-blur-md shrink-0 shadow-xs hover:shadow-sm transition-shadow">
            <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                    {getPageTitle(pathname)}
                </h1>
            </div>

            <DropdownMenu>
                {/* @ts-expect-error asChild Radix compatibility */}
                <DropdownMenuTrigger asChild>
                    <button className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-accent transition-all duration-200 group">
                        <Avatar className="h-8 w-8 border-2 border-border/50 group-hover:border-primary/30 transition-colors">
                            <AvatarFallback className="bg-gradient-to-br from-primary to-primary/70 text-primary-foreground text-xs font-semibold">
                                {initials}
                            </AvatarFallback>
                        </Avatar>
                        <div className="hidden sm:block text-left">
                            <p className="text-sm font-semibold text-foreground">
                                {user?.full_name?.split(" ")[0] ?? "Usuário"}
                            </p>
                            <p className="text-xs text-muted-foreground">{user?.email?.split("@")[0]}</p>
                        </div>
                    </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-52 rounded-xl">
                    <div className="px-3 py-2 bg-gradient-to-r from-primary/10 to-transparent rounded-lg m-1">
                        <p className="font-semibold truncate text-sm">{user?.full_name ?? "Usuário"}</p>
                        <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
                    </div>
                    <DropdownMenuSeparator className="my-1" />
                    <DropdownMenuItem className="rounded-lg mx-1 transition-all">
                        <User className="mr-2 h-4 w-4" />
                        <span>Perfil</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem className="rounded-lg mx-1 transition-all">
                        <Settings className="mr-2 h-4 w-4" />
                        <span>Configurações</span>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="my-1" />
                    <DropdownMenuItem onClick={handleLogout} className="rounded-lg mx-1 text-destructive focus:text-destructive focus:bg-destructive/10 transition-all">
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>Sair</span>
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </header>
    );
}
