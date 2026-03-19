import type { ReactNode } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex">
      {/* Left panel - visible on lg+ */}
      <div className="hidden lg:flex lg:w-1/2 bg-gray-900 text-white flex-col justify-between p-12">
        <div>
          <span className="text-2xl font-bold tracking-tight">FinControl</span>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="text-3xl font-bold leading-tight">
              Tome o controle das suas finanças
            </h2>
            <p className="mt-3 text-gray-400 text-lg">
              Gerencie contas, transações, categorias e metas em um só lugar.
            </p>
          </div>

          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-500/20 text-green-400 text-xs font-bold">
                ✓
              </span>
              <div>
                <p className="font-medium">Visão completa do seu patrimônio</p>
                <p className="text-sm text-gray-400">
                  Acompanhe todas as suas contas em tempo real
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-500/20 text-green-400 text-xs font-bold">
                ✓
              </span>
              <div>
                <p className="font-medium">Relatórios e gráficos detalhados</p>
                <p className="text-sm text-gray-400">
                  Entenda para onde vai o seu dinheiro
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-500/20 text-green-400 text-xs font-bold">
                ✓
              </span>
              <div>
                <p className="font-medium">Metas financeiras personalizadas</p>
                <p className="text-sm text-gray-400">
                  Defina e alcance seus objetivos com facilidade
                </p>
              </div>
            </li>
          </ul>
        </div>

        <p className="text-sm text-gray-500">
          &copy; {new Date().getFullYear()} FinControl. Todos os direitos
          reservados.
        </p>
      </div>

      {/* Right panel - form area */}
      <div className="flex flex-1 items-center justify-center p-6 bg-white">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}
