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
  cpf: string;
  password: string;
}

interface AuthResponse {
  user: {
    id: string;
    email: string;
    cpf: string;
    full_name: string;
    tenant_id: string;
    has_completed_onboarding: boolean;
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
      setAuth(data.user);
      if (data.user.has_completed_onboarding) {
        router.push("/dashboard");
      } else {
        router.push("/onboarding");
      }
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
      setAuth(data.user);
      router.push("/onboarding");
    },
  });
}

export function useCompleteOnboarding() {
  const { user, setUser } = useAuthStore();
  const router = useRouter();

  return useMutation({
    mutationFn: async () => {
      await api.post("/dashboard/complete-onboarding");
    },
    onSuccess: () => {
      if (user) {
        setUser({ ...user, has_completed_onboarding: true });
      }
      router.push("/dashboard");
    },
  });
}

export function useLogout() {
  const { logout } = useAuthStore();
  const router = useRouter();

  return async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // Ignorar erros no logout
    } finally {
      logout();
      router.push("/login");
    }
  };
}
