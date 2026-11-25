"use client";

import { useActionState, useState } from "react";
import { search, type Result } from "./actions";

export default function Page() {
  const [result, action, pending] = useActionState(search, { status: "idle" } as Result);
  const [query, setQuery] = useState("");
  return <main>
    <h1>Pesquisa no PubMed</h1>
    <form action={action}>
      <label htmlFor="query">Tema de pesquisa</label>
      <div className="controls"><input id="query" name="query" type="search" value={query}
        onChange={event => setQuery(event.target.value)} required maxLength={300}
        aria-describedby="privacy" placeholder="Ex.: qualidade do sono" />
        <button disabled={pending}>{pending ? "Pesquisando…" : "Pesquisar"}</button></div>
      <small id="privacy">Use apenas termos bibliográficos. Nunca informe dados de pacientes.</small>
    </form>
    <section aria-live="polite" aria-busy={pending}>
      {!pending && result.status === "error" && <p role="alert">{result.message}</p>}
      {!pending && result.status === "ok" && <>
        <h2>{result.articles.length ? "Publicações encontradas" : "Nenhuma publicação encontrada"}</h2>
        {result.cached && <p>Resultado recuperado do cache.</p>}
        {result.articles.map(article => <article key={article.pmid}>
          <h3><a href={`https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(article.pmid)}/`}>{article.title || "Publicação sem título"}</a></h3>
          <p>PMID {article.pmid}{article.doi && <> · DOI {article.doi}</>}</p>
          <small>Recuperado em {new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(article.retrieved_at))} (UTC)</small>
        </article>)}
      </>}
    </section>
  </main>;
}
