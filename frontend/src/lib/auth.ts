import { api } from "./api";

interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

interface UserResponse {
    id: string;
    email: string;
    full_name: string | null;
    is_active: boolean;
    is_verified: boolean;
    tenant_id: string;
    created_at: string;
}

export async function loginApi(email: string, password: string) {
    const { data } = await api.post<TokenResponse>("/auth/login", {
        email,
        password,
    });
    return data;
}

export async function registerApi(
    email: string,
    password: string,
    full_name?: string
) {
    const { data } = await api.post<TokenResponse>("/auth/register", {
        email,
        password,
        full_name,
    });
    return data;
}

export async function refreshTokenApi(refreshToken: string) {
    const { data } = await api.post<TokenResponse>("/auth/refresh", {
        refresh_token: refreshToken,
    });
    return data;
}

export async function fetchMe() {
    const { data } = await api.get<UserResponse>("/auth/me");
    return data;
}

export async function logoutApi() {
    try {
        await api.post("/auth/logout");
    } catch (error) {
        // Ignore errors during logout - just clear local state
        console.warn("Logout API call failed", error);
    }
}
