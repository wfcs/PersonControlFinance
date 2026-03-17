import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { loginApi, registerApi, fetchMe, logoutApi } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";

/* ── Types ──────────────────────────────────────────────────────── */
export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    full_name?: string;
}

export interface UserProfile {
    id: string;
    email: string;
    full_name: string | null;
    is_active: boolean;
    is_verified: boolean;
    tenant_id: string;
    created_at: string;
}

/* ── Hooks ──────────────────────────────────────────────────────── */
export function useLogin() {
    const setTokens = useAuthStore((s) => s.setTokens);
    const setUser = useAuthStore((s) => s.setUser);

    return useMutation({
        mutationFn: async (credentials: LoginRequest) => {
            const tokens = await loginApi(credentials.email, credentials.password);
            return tokens;
        },
        onSuccess: async (tokens) => {
            setTokens(tokens.access_token, tokens.refresh_token);
            // Fetch user profile after login
            const user = await fetchMe();
            setUser({
                id: user.id,
                email: user.email,
                full_name: user.full_name,
                tenant_id: user.tenant_id,
            });
        },
    });
}

export function useRegister() {
    const setTokens = useAuthStore((s) => s.setTokens);
    const setUser = useAuthStore((s) => s.setUser);

    return useMutation({
        mutationFn: async (credentials: RegisterRequest) => {
            const tokens = await registerApi(
                credentials.email,
                credentials.password,
                credentials.full_name
            );
            return tokens;
        },
        onSuccess: async (tokens) => {
            setTokens(tokens.access_token, tokens.refresh_token);
            const user = await fetchMe();
            setUser({
                id: user.id,
                email: user.email,
                full_name: user.full_name,
                tenant_id: user.tenant_id,
            });
        },
    });
}

export function useMe() {
    const user = useAuthStore((s) => s.user);
    const setUser = useAuthStore((s) => s.setUser);

    return useQuery({
        queryKey: ["auth", "me"],
        queryFn: async () => {
            const profile = await fetchMe();
            setUser({
                id: profile.id,
                email: profile.email,
                full_name: profile.full_name,
                tenant_id: profile.tenant_id,
            });
            return profile;
        },
        staleTime: 5 * 60 * 1000, // 5 minutes
        enabled: !!user,
    });
}

export function useLogout() {
    const qc = useQueryClient();
    const logout = useAuthStore((s) => s.logout);

    return useMutation({
        mutationFn: async () => {
            await logoutApi();
        },
        onSuccess: () => {
            logout();
            qc.clear();
            if (typeof window !== "undefined") {
                window.location.href = "/login";
            }
        },
        onError: () => {
            // Even if logout API fails, clear local state
            logout();
            qc.clear();
            if (typeof window !== "undefined") {
                window.location.href = "/login";
            }
        },
    });
}

export function useAuthStatus() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated());
    const user = useAuthStore((s) => s.user);
    const accessToken = useAuthStore((s) => s.accessToken);

    return {
        isAuthenticated,
        user,
        accessToken,
    };
}
