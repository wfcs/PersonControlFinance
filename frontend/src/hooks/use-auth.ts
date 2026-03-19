"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

interface LoginPayload {
  email: string;
  password: string;
}

interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  tenant_name: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    tenant_id: string;
  };
}

export function useLogin() {
  const { setAuth } = useAuthStore();
  const router = useRouter();

  return useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const { data } = await api.post<AuthResponse>("/auth/login", payload);
      return data;
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      router.push("/dashboard");
    },
  });
}

export function useRegister() {
  const { setAuth } = useAuthStore();
  const router = useRouter();

  return useMutation({
    mutationFn: async (payload: RegisterPayload) => {
      const { data } = await api.post<AuthResponse>("/auth/register", payload);
      return data;
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      router.push("/dashboard");
    },
  });
}

export function useLogout() {
  const { logout } = useAuthStore();
  const router = useRouter();

  return () => {
    logout();
    router.push("/login");
  };
}
