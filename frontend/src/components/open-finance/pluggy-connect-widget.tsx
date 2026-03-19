"use client";

import { useState, useCallback } from "react";
import {
  usePluggyStatus,
  useCreateConnectToken,
  useOnItemConnected,
  useSyncItem,
  useDisconnectItem,
} from "@/hooks/use-open-finance";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogPortal,
  DialogBackdrop,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  Link2,
  Unlink,
  RefreshCw,
  ExternalLink,
  Loader2,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";

export function PluggyConnectButton() {
  const [widgetOpen, setWidgetOpen] = useState(false);
  const [connectToken, setConnectToken] = useState<string | null>(null);
  const [widgetError, setWidgetError] = useState<string | null>(null);

  const { data: status, isLoading: statusLoading } = usePluggyStatus();
  const createToken = useCreateConnectToken();
  const onItemConnected = useOnItemConnected();

  const handleOpenWidget = useCallback(async () => {
    setWidgetError(null);
    try {
      const result = await createToken.mutateAsync({});
      setConnectToken(result.access_token);
      setWidgetOpen(true);
    } catch {
      setWidgetError("Erro ao gerar token de conexão. Tente novamente.");
    }
  }, [createToken]);

  const handleItemConnected = useCallback(
    async (itemId: string) => {
      try {
        await onItemConnected.mutateAsync({ item_id: itemId });
        setWidgetOpen(false);
        setConnectToken(null);
      } catch {
        setWidgetError("Erro ao sincronizar dados bancários.");
      }
    },
    [onItemConnected]
  );

  if (statusLoading) {
    return (
      <Button variant="outline" disabled>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Verificando...
      </Button>
    );
  }

  if (!status?.configured) {
    return (
      <Button variant="outline" disabled title="Open Finance não configurado">
        <AlertTriangle className="mr-2 h-4 w-4 text-yellow-500" />
        Open Finance indisponível
      </Button>
    );
  }

  return (
    <>
      <Button
        variant="outline"
        onClick={handleOpenWidget}
        disabled={createToken.isPending}
        className="border-brand-600 text-brand-600 hover:bg-brand-50"
      >
        {createToken.isPending ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Link2 className="mr-2 h-4 w-4" />
        )}
        Conectar Banco
      </Button>

      {widgetError && (
        <p className="mt-1 text-xs text-red-500">{widgetError}</p>
      )}

      <Dialog open={widgetOpen} onOpenChange={setWidgetOpen}>
        <DialogPortal>
          <DialogBackdrop />
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-brand-600" />
                Conectar Banco via Open Finance
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <p className="text-sm text-gray-500">
                Conecte sua conta bancária de forma segura usando Open Finance.
                Seus dados são criptografados e protegidos.
              </p>

              {connectToken && (
                <PluggyWidgetEmbed
                  connectToken={connectToken}
                  onSuccess={handleItemConnected}
                  onError={() =>
                    setWidgetError("Falha na conexão. Tente novamente.")
                  }
                  onClose={() => setWidgetOpen(false)}
                />
              )}

              {onItemConnected.isPending && (
                <div className="flex items-center justify-center gap-2 py-6">
                  <Loader2 className="h-5 w-5 animate-spin text-brand-600" />
                  <span className="text-sm text-gray-600">
                    Sincronizando contas e transações...
                  </span>
                </div>
              )}
            </div>
          </DialogContent>
        </DialogPortal>
      </Dialog>
    </>
  );
}

function PluggyWidgetEmbed({
  connectToken,
  onSuccess,
  onError,
  onClose,
}: {
  connectToken: string;
  onSuccess: (itemId: string) => void;
  onError: () => void;
  onClose: () => void;
}) {
  // Pluggy Connect Widget via iframe
  // The widget URL accepts the connect token and communicates via postMessage
  const widgetUrl = `https://connect.pluggy.ai?connect_token=${connectToken}`;

  // Listen for postMessage events from the Pluggy widget
  if (typeof window !== "undefined") {
    const handler = (event: MessageEvent) => {
      if (event.origin !== "https://connect.pluggy.ai") return;

      const data = event.data;
      if (data?.event === "close") {
        window.removeEventListener("message", handler);
        onClose();
      } else if (data?.event === "success" && data?.item?.id) {
        window.removeEventListener("message", handler);
        onSuccess(data.item.id);
      } else if (data?.event === "error") {
        window.removeEventListener("message", handler);
        onError();
      }
    };
    window.addEventListener("message", handler);
  }

  return (
    <div className="overflow-hidden rounded-lg border">
      <iframe
        src={widgetUrl}
        width="100%"
        height="450"
        style={{ border: "none" }}
        allow="camera"
        title="Pluggy Connect"
      />
    </div>
  );
}

export function ConnectedItemCard({
  itemId,
  accountCount,
}: {
  itemId: string;
  accountCount?: number;
}) {
  const syncItem = useSyncItem();
  const disconnectItem = useDisconnectItem();
  const [confirmDisconnect, setConfirmDisconnect] = useState(false);

  return (
    <Card className="border-brand-200 bg-brand-50/30">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm">
            <ShieldCheck className="h-4 w-4 text-brand-600" />
            Conexão Open Finance
          </CardTitle>
          <Badge variant="secondary" className="bg-brand-100 text-brand-700 text-xs">
            Conectado
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="mb-3 text-xs text-gray-500">
          ID: {itemId.slice(0, 8)}...
          {accountCount !== undefined && ` · ${accountCount} conta(s)`}
        </p>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => syncItem.mutate(itemId)}
            disabled={syncItem.isPending}
            className="text-xs"
          >
            {syncItem.isPending ? (
              <Loader2 className="mr-1 h-3 w-3 animate-spin" />
            ) : (
              <RefreshCw className="mr-1 h-3 w-3" />
            )}
            Sincronizar
          </Button>

          {confirmDisconnect ? (
            <div className="flex gap-1">
              <Button
                size="sm"
                variant="destructive"
                onClick={() => {
                  disconnectItem.mutate(itemId);
                  setConfirmDisconnect(false);
                }}
                disabled={disconnectItem.isPending}
                className="text-xs"
              >
                {disconnectItem.isPending ? (
                  <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                ) : (
                  "Confirmar"
                )}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setConfirmDisconnect(false)}
                className="text-xs"
              >
                Cancelar
              </Button>
            </div>
          ) : (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setConfirmDisconnect(true)}
              className="text-xs text-red-500 hover:text-red-600"
            >
              <Unlink className="mr-1 h-3 w-3" />
              Desconectar
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function OpenFinanceSection() {
  const { data: status, isLoading } = usePluggyStatus();

  if (isLoading) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-brand-600" />
          <h3 className="text-sm font-semibold text-gray-700">Open Finance</h3>
        </div>
        {status?.configured && (
          <a
            href="https://pluggy.ai"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600"
          >
            Powered by Pluggy
            <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>

      {status?.configured ? (
        <div className="rounded-lg border bg-brand-50/30 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">
                {status.connected_items > 0
                  ? `${status.connected_items} conexão(ões) ativa(s)`
                  : "Nenhum banco conectado"}
              </p>
              <p className="text-xs text-gray-500">
                Conecte seu banco para importar contas e transações automaticamente
              </p>
            </div>
            <PluggyConnectButton />
          </div>
        </div>
      ) : (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <p className="text-sm text-yellow-700">
              Open Finance não está configurado. Configure as credenciais Pluggy nas variáveis de ambiente.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
