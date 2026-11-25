import { NextRequest, NextResponse } from "next/server";
export const runtime = "nodejs";
const modes = new Set(["pubmed","index","semantic","context"]);
export async function POST(req: NextRequest) {
 const origin = req.headers.get("origin");
 const expected = process.env.MEDJON_WEB_ORIGIN || "http://localhost:3000";
 if (origin !== expected) return NextResponse.json({error:"Origem não autorizada"},{status:403});
 const key = process.env.MEDJON_API_KEY;
 if (!key) return NextResponse.json({error:"Servidor não configurado"},{status:503});
 try {
  const raw = await req.text();
  if (raw.length > 4096) return NextResponse.json({error:"Requisição extensa"},{status:413});
  const {mode,query,limit,bibliographic_only} = JSON.parse(raw);
  if (!modes.has(mode) || typeof query !== "string" || query.trim().length < 2 || query.length > 500 || !Number.isInteger(limit) || limit < 1 || limit > 20 || bibliographic_only !== true)
   return NextResponse.json({error:"Consulta inválida"},{status:400});
  const upstream = await fetch((process.env.MEDJON_BACKEND_URL || "http://api:8000")+"/research/"+mode,{method:"POST",headers:{"Content-Type":"application/json","X-API-Key":key},body:JSON.stringify({query,limit,bibliographic_only}),cache:"no-store",signal:AbortSignal.timeout(150000)});
  if (!upstream.ok) return NextResponse.json({error:"Serviço de pesquisa indisponível"},{status:502});
  return NextResponse.json(await upstream.json(),{headers:{"Cache-Control":"no-store"}});
 } catch { return NextResponse.json({error:"Não foi possível concluir a consulta"},{status:502}); }
}