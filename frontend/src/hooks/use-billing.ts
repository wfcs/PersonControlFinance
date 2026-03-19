import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

interface SubscriptionStatus {
  tenant_id: string;
  plan: string;
  subscription_status: string;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
}

interface CheckoutResponse {
  checkout_url: string;
}

interface PortalResponse {
  portal_url: string;
}

export function useSubscriptionStatus() {
  return useQuery<SubscriptionStatus>({
    queryKey: ["billing", "status"],
    queryFn: async () => {
      const { data } = await api.get("/billing/status");
      return data;
    },
  });
}

export function useCreateCheckout() {
  return useMutation<CheckoutResponse, Error, { price_id: string }>({
    mutationFn: async (payload) => {
      const { data } = await api.post("/billing/checkout", {
        price_id: payload.price_id,
        success_url: `${window.location.origin}/plans?success=true`,
        cancel_url: `${window.location.origin}/plans?canceled=true`,
      });
      return data;
    },
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });
}

export function useCreatePortal() {
  return useMutation<PortalResponse, Error>({
    mutationFn: async () => {
      const { data } = await api.post("/billing/portal", {
        return_url: `${window.location.origin}/plans`,
      });
      return data;
    },
    onSuccess: (data) => {
      window.location.href = data.portal_url;
    },
  });
}
