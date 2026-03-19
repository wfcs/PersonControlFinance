"use client";

import { usePathname } from "next/navigation";
import { Menu, User, LogOut } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/stores/auth-store";
import { useLogout } from "@/hooks";

const routeLabels: Record<string, string> = {
  "/dashboard": "Visão Geral",
  "/transactions": "Transações",
  "/accounts": "Contas",
  "/categories": "Categorias",
  "/recurring": "Recorrentes",
  "/cash-flow": "Fluxo de Caixa",
  "/invoices": "Faturas",
  "/goals": "Metas",
  "/projection": "Projeção",
  "/net-worth": "Patrimônio",
  "/reports": "Relatórios",
  "/plans": "Planos",
};

function getRouteLabel(pathname: string): string {
  for (const [route, label] of Object.entries(routeLabels)) {
    if (pathname === route || (route !== "/dashboard" && pathname.startsWith(route))) {
      return label;
    }
  }
  return "FinControl";
}

function getInitials(name: string | undefined): string {
  if (!name) return "U";
  return name
    .split(" ")
    .slice(0, 2)
    .map((n) => n[0])
    .join("")
    .toUpperCase();
}

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();
  const pageTitle = getRouteLabel(pathname);

  return (
    <header className="flex items-center justify-between h-14 px-4 md:px-6 border-b bg-white shrink-0">
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMenuClick}
          aria-label="Abrir menu"
        >
          <Menu size={20} />
        </Button>
        <h1 className="text-base font-semibold text-gray-900">{pageTitle}</h1>
      </div>

      {/* User dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full p-0">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-blue-500 text-white text-xs">
                {getInitials(user?.full_name)}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-52" align="end">
          <div className="px-3 py-2">
            <p className="text-sm font-medium leading-none truncate">
              {user?.full_name ?? "Usuário"}
            </p>
            <p className="text-xs text-muted-foreground mt-1 truncate">
              {user?.email ?? ""}
            </p>
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <User className="mr-2 h-4 w-4" />
            Perfil
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            className="text-red-600 focus:text-red-600"
            onClick={() => logout()}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Sair
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
