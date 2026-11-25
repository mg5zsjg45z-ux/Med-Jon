"use server";

export type Article = {
  pmid: string;
  title: string | null;
  year_or_date: string | null;
  doi: string | null;
  retrieved_at: string;
};
export type Result =
  | { status: "idle" }
  | { status: "error"; message: string }
  | { status: "ok"; articles: Article[]; cached: boolean };

export async function search(_: Result, form: FormData): Promise<Result> {
  const query = String(form.get("query") ?? "").trim();
  if (!query || query.length > 300)
    return { status: "error", message: "Informe um tema de até 300 caracteres." };
  try {
    const response = await fetch(`${process.env.API_ORIGIN || "http://127.0.0.1:8000"}/api/pubmed/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
      cache: "no-store",
      signal: AbortSignal.timeout(50000),
    });
    if (response.ok) {
      const { articles, cached } = await response.json();
      return { status: "ok", articles, cached };
    }
    if (response.status === 429)
      return { status: "error", message: "Aguarde um instante antes de pesquisar novamente." };
    if (response.status === 502)
      return { status: "error", message: "O PubMed está temporariamente indisponível. Tente novamente." };
  } catch {
    // A interface também precisa lidar com indisponibilidade da API local.
  }
  return { status: "error", message: "O serviço de pesquisa está indisponível. Tente novamente." };
}
