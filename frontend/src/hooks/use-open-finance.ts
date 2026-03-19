import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

interface PluggyStatus {
  configured: boolean;
  connected_items: number;
}

interface ConnectTokenResponse {
  access_token: string;
}

interface SyncResponse {
  accounts_synced: number;
  transactions_imported: number;
}

export function usePluggyStatus() {
  return useQuery<PluggyStatus>({
    queryKey: ["open-finance", "status"],
    queryFn: async () => {
      const { data } = await api.get("/open-finance/status");
      return data;
    },
  });
}

export function useCreateConnectToken() {
  return useMutation<ConnectTokenResponse, Error, { item_id?: string }>({
    mutationFn: async (payload) => {
      const { data } = await api.post("/open-finance/connect-token", payload);
      return data;
    },
  });
}

export function useOnItemConnected() {
  const queryClient = useQueryClient();
  return useMutation<SyncResponse, Error, { item_id: string }>({
    mutationFn: async (payload) => {
      const { data } = await api.post("/open-finance/connect", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["open-finance"] });
    },
  });
}

export function useSyncItem() {
  const queryClient = useQueryClient();
  return useMutation<SyncResponse, Error, string>({
    mutationFn: async (itemId) => {
      const { data } = await api.post(`/open-finance/sync/${itemId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}

export function useDisconnectItem() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: async (itemId) => {
      await api.delete(`/open-finance/disconnect/${itemId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["open-finance"] });
    },
  });
}
