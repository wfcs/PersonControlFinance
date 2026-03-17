"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Building2,
    Users,
    Wallet,
    ArrowLeftRight,
    Loader2,
    ShieldAlert,
} from "lucide-react";

/* ── Types ─────────────────────────────────────────────────────── */
interface AdminStats {
    total_tenants: number;
    total_users: number;
    total_accounts: number;
    total_transactions: number;
    by_plan: Record<string, number>;
}

interface Tenant {
    id: string;
    name: string;
    plan: string;
    subscription_status: string;
    user_count: number;
    account_count: number;
    created_at: string;
}

interface AdminUser {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    is_verified: boolean;
    tenant_name: string;
    created_at: string;
}

/* ── Hooks ─────────────────────────────────────────────────────── */
function useAdminStats() {
    return useQuery<AdminStats>({
        queryKey: ["admin", "stats"],
        queryFn: async () => (await api.get("/admin/stats")).data,
    });
}

function useAdminTenants() {
    return useQuery<Tenant[]>({
        queryKey: ["admin", "tenants"],
        queryFn: async () => (await api.get("/admin/tenants")).data,
    });
}

function useAdminUsers() {
    return useQuery<AdminUser[]>({
        queryKey: ["admin", "users"],
        queryFn: async () => (await api.get("/admin/users")).data,
    });
}

function useUpdateTenant() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async ({
            id,
            plan,
        }: {
            id: string;
            plan: string;
        }) => {
            await api.patch(`/admin/tenants/${id}`, { plan });
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["admin"] });
        },
    });
}

function useToggleUser() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async ({
            id,
            is_active,
        }: {
            id: string;
            is_active: boolean;
        }) => {
            await api.patch(`/admin/users/${id}`, { is_active });
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["admin", "users"] });
        },
    });
}

/* ── Stats Card ────────────────────────────────────────────────── */
function StatCard({
    label,
    value,
    icon: Icon,
}: {
    label: string;
    value: number | string;
    icon: React.ComponentType<{ className?: string }>;
}) {
    return (
        <div className="bg-card border rounded-xl p-5">
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">{label}</span>
                <Icon className="h-4 w-4 text-muted-foreground" />
            </div>
            <p className="text-2xl font-bold">{value}</p>
        </div>
    );
}

/* ── Page ──────────────────────────────────────────────────────── */
export default function AdminPage() {
    const stats = useAdminStats();
    const tenants = useAdminTenants();
    const users = useAdminUsers();
    const updateTenant = useUpdateTenant();
    const toggleUser = useToggleUser();
    const [tab, setTab] = useState<"tenants" | "users">("tenants");

    // Handle 403 — not admin
    if (
        stats.error &&
        (stats.error as { response?: { status?: number } })?.response
            ?.status === 403
    ) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
                <ShieldAlert className="h-16 w-16 text-destructive" />
                <h2 className="text-xl font-bold">Acesso restrito</h2>
                <p className="text-muted-foreground text-sm text-center max-w-sm">
                    Você não tem permissão para acessar o painel
                    administrativo. Esta área é restrita a administradores.
                </p>
            </div>
        );
    }

    if (stats.isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    const s = stats.data;

    return (
        <div className="p-6 space-y-6 max-w-6xl mx-auto">
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    label="Tenants"
                    value={s?.total_tenants ?? 0}
                    icon={Building2}
                />
                <StatCard
                    label="Usuários"
                    value={s?.total_users ?? 0}
                    icon={Users}
                />
                <StatCard
                    label="Contas"
                    value={s?.total_accounts ?? 0}
                    icon={Wallet}
                />
                <StatCard
                    label="Transações"
                    value={s?.total_transactions ?? 0}
                    icon={ArrowLeftRight}
                />
            </div>

            {/* Plan distribution */}
            {s?.by_plan && Object.keys(s.by_plan).length > 0 && (
                <div className="bg-card border rounded-xl p-5">
                    <h3 className="text-sm font-semibold mb-3">
                        Distribuição por plano
                    </h3>
                    <div className="flex gap-4 flex-wrap">
                        {Object.entries(s.by_plan).map(([plan, count]) => (
                            <div
                                key={plan}
                                className="px-3 py-1.5 bg-muted rounded-lg text-sm"
                            >
                                <span className="font-medium capitalize">
                                    {plan}
                                </span>
                                :{" "}
                                <span className="text-muted-foreground">
                                    {count}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="flex gap-2 border-b pb-2">
                <button
                    onClick={() => setTab("tenants")}
                    className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                        tab === "tenants"
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:text-foreground"
                    }`}
                >
                    Tenants
                </button>
                <button
                    onClick={() => setTab("users")}
                    className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                        tab === "users"
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:text-foreground"
                    }`}
                >
                    Usuários
                </button>
            </div>

            {/* Tenants Table */}
            {tab === "tenants" && (
                <div className="bg-card border rounded-xl overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b text-left">
                                <th className="px-4 py-3 font-medium">Nome</th>
                                <th className="px-4 py-3 font-medium">Plano</th>
                                <th className="px-4 py-3 font-medium">
                                    Status
                                </th>
                                <th className="px-4 py-3 font-medium">
                                    Usuários
                                </th>
                                <th className="px-4 py-3 font-medium">
                                    Contas
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {tenants.data?.map((t) => (
                                <tr
                                    key={t.id}
                                    className="border-b last:border-0"
                                >
                                    <td className="px-4 py-3 font-medium">
                                        {t.name}
                                    </td>
                                    <td className="px-4 py-3">
                                        <Select
                                            defaultValue={t.plan}
                                            onValueChange={(plan) =>
                                                updateTenant.mutate({
                                                    id: t.id,
                                                    plan,
                                                })
                                            }
                                        >
                                            <SelectTrigger className="w-28 h-8">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="free">
                                                    Free
                                                </SelectItem>
                                                <SelectItem value="starter">
                                                    Starter
                                                </SelectItem>
                                                <SelectItem value="pro">
                                                    Pro
                                                </SelectItem>
                                                <SelectItem value="enterprise">
                                                    Enterprise
                                                </SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span
                                            className={`px-2 py-1 rounded text-xs font-medium ${
                                                t.subscription_status ===
                                                "active"
                                                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                                                    : "bg-muted text-muted-foreground"
                                            }`}
                                        >
                                            {t.subscription_status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        {t.user_count}
                                    </td>
                                    <td className="px-4 py-3">
                                        {t.account_count}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {tenants.isLoading && (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin text-primary" />
                        </div>
                    )}
                </div>
            )}

            {/* Users Table */}
            {tab === "users" && (
                <div className="bg-card border rounded-xl overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b text-left">
                                <th className="px-4 py-3 font-medium">Nome</th>
                                <th className="px-4 py-3 font-medium">
                                    E-mail
                                </th>
                                <th className="px-4 py-3 font-medium">
                                    Tenant
                                </th>
                                <th className="px-4 py-3 font-medium">
                                    Status
                                </th>
                                <th className="px-4 py-3 font-medium">Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.data?.map((u) => (
                                <tr
                                    key={u.id}
                                    className="border-b last:border-0"
                                >
                                    <td className="px-4 py-3 font-medium">
                                        {u.full_name}
                                    </td>
                                    <td className="px-4 py-3 text-muted-foreground">
                                        {u.email}
                                    </td>
                                    <td className="px-4 py-3">
                                        {u.tenant_name}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span
                                            className={`px-2 py-1 rounded text-xs font-medium ${
                                                u.is_active
                                                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                                                    : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                            }`}
                                        >
                                            {u.is_active
                                                ? "Ativo"
                                                : "Inativo"}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() =>
                                                toggleUser.mutate({
                                                    id: u.id,
                                                    is_active: !u.is_active,
                                                })
                                            }
                                        >
                                            {u.is_active
                                                ? "Desativar"
                                                : "Ativar"}
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {users.isLoading && (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin text-primary" />
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
