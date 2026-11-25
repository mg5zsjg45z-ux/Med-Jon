import "./style.css";
import type { ReactNode } from "react";

export const metadata = { title: "Pesquisa PubMed | Med-Jon" };

export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="pt-BR"><body><header><strong>Med-Jon</strong><span>Biblioteca de evidências</span></header>{children}</body></html>;
}
