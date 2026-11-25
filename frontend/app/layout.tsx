import type { Metadata } from "next";
import "./style.css";
export const metadata: Metadata = {title:"Med-Jon | Pesquisa médica",description:"Protótipo de pesquisa bibliográfica"};
export default function Layout({children}:{children:React.ReactNode}) {
 return <html lang="pt-BR"><body>{children}</body></html>;
}