/**
 * kaibau-gateway — OpenAI-compatible Cloudflare Worker
 * Routes: venice/*, featherless/*, grok/* (also venice-*, featherless-*, grok-*)
 * Hard rules: 18+, no minors, per-agent no-repeat note
 */

const HARD_RULES = [
  "HARD RULES (non-negotiable):",
  "1. All content and characters MUST be 18+ adults only. Never depict or involve minors (anyone under 18) in sexual, romantic, or exploitative contexts.",
  "2. Refuse any request that sexualizes minors; respond briefly that it is illegal and stop.",
  "3. Do not repeat the same long passage verbatim for the same agent session when a no-repeat note is present — vary phrasing and advance the scene.",
].join("\n");

const PROVIDERS = {
  venice: {
    baseUrl: "https://api.venice.ai/api/v1",
    keyEnv: "VENICE_API_KEY",
    label: "Venice AI",
  },
  featherless: {
    baseUrl: "https://api.featherless.ai/v1",
    keyEnv: "FEATHERLESS_API_KEY",
    label: "Featherless",
  },
  grok: {
    baseUrl: "https://api.x.ai/v1",
    keyEnv: "XAI_API_KEY",
    label: "xAI Grok",
  },
};

/** Parse provider + upstream model id from client model string */
function parseModel(model) {
  if (!model || typeof model !== "string") return null;
  const m = model.trim();
  const slash = m.match(/^(venice|featherless|grok)[\/:](.+)$/i);
  if (slash) {
    return { provider: slash[1].toLowerCase(), upstreamModel: slash[2] };
  }
  const dash = m.match(/^(venice|featherless|grok)-(.+)$/i);
  if (dash) {
    return { provider: dash[1].toLowerCase(), upstreamModel: dash[2] };
  }
  const bare = m.toLowerCase();
  if (PROVIDERS[bare]) {
    return { provider: bare, upstreamModel: bare };
  }
  return null;
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers":
      "Content-Type, Authorization, X-User-Id, X-Agent-Id, X-Request-Id",
  };
}

function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(),
      ...extra,
    },
  });
}

function extractIds(request, body) {
  const h = request.headers;
  const meta = (body && body.metadata) || {};
  return {
    userId:
      h.get("X-User-Id") ||
      h.get("x-user-id") ||
      meta.user_id ||
      meta.userId ||
      null,
    agentId:
      h.get("X-Agent-Id") ||
      h.get("x-agent-id") ||
      meta.agent_id ||
      meta.agentId ||
      null,
  };
}

async function recallMemory(env, { userId, agentId, query }) {
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE) return "";
  if (!userId && !agentId) return "";

  const base = String(env.SUPABASE_URL).replace(/\/$/, "");
  const headers = {
    apikey: env.SUPABASE_SERVICE_ROLE,
    Authorization: `Bearer ${env.SUPABASE_SERVICE_ROLE}`,
    "Content-Type": "application/json",
  };

  try {
    const rpcRes = await fetch(`${base}/rest/v1/rpc/lewka_search_pages`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        p_user_id: userId,
        p_agent_id: agentId,
        p_query: query || "",
        p_limit: 5,
      }),
    });
    if (rpcRes.ok) {
      const rows = await rpcRes.json();
      if (Array.isArray(rows) && rows.length) {
        return rows
          .map((r) => r.content || r.snippet || r.text || JSON.stringify(r))
          .join("\n---\n")
          .slice(0, 4000);
      }
    }
  } catch (_) {}

  try {
    const params = new URLSearchParams();
    params.set("select", "content,created_at");
    params.set("order", "created_at.desc");
    params.set("limit", "5");
    if (agentId) params.set("agent_id", `eq.${agentId}`);
    else if (userId) params.set("user_id", `eq.${userId}`);

    const memRes = await fetch(`${base}/rest/v1/memories?${params}`, {
      method: "GET",
      headers,
    });
    if (memRes.ok) {
      const rows = await memRes.json();
      if (Array.isArray(rows) && rows.length) {
        return rows
          .map((r) => r.content || "")
          .filter(Boolean)
          .join("\n---\n")
          .slice(0, 4000);
      }
    }
  } catch (_) {}

  return "";
}

function injectSystemRules(messages, { agentId, memoryText }) {
  const parts = [HARD_RULES];
  if (agentId) {
    parts.push(
      `Agent session id: ${agentId}. Avoid repeating prior long passages for this agent; advance the scene instead.`
    );
  }
  if (memoryText) {
    parts.push(`Relevant memory recall (stub):\n${memoryText}`);
  }
  const systemContent = parts.join("\n\n");

  const out = Array.isArray(messages) ? [...messages] : [];
  const firstSystemIdx = out.findIndex((m) => m && m.role === "system");
  if (firstSystemIdx >= 0) {
    const prev = out[firstSystemIdx];
    out[firstSystemIdx] = {
      ...prev,
      content: `${systemContent}\n\n${prev.content || ""}`,
    };
  } else {
    out.unshift({ role: "system", content: systemContent });
  }
  return out;
}

function lastUserText(messages) {
  if (!Array.isArray(messages)) return "";
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (m && m.role === "user") {
      if (typeof m.content === "string") return m.content;
      if (Array.isArray(m.content)) {
        return m.content
          .filter((p) => p && p.type === "text")
          .map((p) => p.text)
          .join(" ");
      }
    }
  }
  return "";
}

async function handleModels() {
  const data = [];
  for (const [id, p] of Object.entries(PROVIDERS)) {
    data.push({
      id: `${id}/default`,
      object: "model",
      created: 0,
      owned_by: p.label,
    });
  }
  data.push({
    id: "venice/* | featherless/* | grok/* (also dash/colon forms)",
    object: "model",
    created: 0,
    owned_by: "kaibau-gateway",
  });
  return json({ object: "list", data });
}

async function handleChatCompletions(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: { message: "Invalid JSON body", type: "invalid_request_error" } }, 400);
  }

  const parsed = parseModel(body.model);
  if (!parsed || !PROVIDERS[parsed.provider]) {
    return json(
      {
        error: {
          message:
            "Unknown model. Use venice/<id>, featherless/<id>, or grok/<id> (also venice-*, etc.)",
          type: "invalid_request_error",
        },
      },
      400
    );
  }

  const provider = PROVIDERS[parsed.provider];
  const apiKey = env[provider.keyEnv];
  if (!apiKey) {
    return json(
      {
        error: {
          message: `${provider.label} not configured: missing secret ${provider.keyEnv}. Set via wrangler secret put ${provider.keyEnv}`,
          type: "upstream_unavailable",
          code: "provider_not_configured",
        },
      },
      503
    );
  }

  const { userId, agentId } = extractIds(request, body);
  const memoryText = await recallMemory(env, {
    userId,
    agentId,
    query: lastUserText(body.messages),
  });

  const upstreamBody = {
    ...body,
    model: parsed.upstreamModel,
    messages: injectSystemRules(body.messages, { agentId, memoryText }),
  };
  delete upstreamBody.metadata;

  const upstreamUrl = `${provider.baseUrl}/chat/completions`;
  let upstreamRes;
  try {
    upstreamRes = await fetch(upstreamUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(upstreamBody),
    });
  } catch (e) {
    return json(
      {
        error: {
          message: `Failed to reach ${provider.label}: ${e.message || String(e)}`,
          type: "upstream_error",
        },
      },
      502
    );
  }

  const ct = upstreamRes.headers.get("Content-Type") || "";
  if (body.stream && ct.includes("text/event-stream")) {
    return new Response(upstreamRes.body, {
      status: upstreamRes.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        ...corsHeaders(),
        "X-Gateway-Provider": parsed.provider,
        "X-Gateway-User-Id": userId || "",
        "X-Gateway-Agent-Id": agentId || "",
      },
    });
  }

  const text = await upstreamRes.text();
  return new Response(text, {
    status: upstreamRes.status,
    headers: {
      "Content-Type": ct.includes("json") ? "application/json" : ct || "application/json",
      ...corsHeaders(),
      "X-Gateway-Provider": parsed.provider,
      "X-Gateway-User-Id": userId || "",
      "X-Gateway-Agent-Id": agentId || "",
    },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (request.method === "GET" && (path === "/v1/models" || path === "/models")) {
      return handleModels();
    }

    if (
      request.method === "POST" &&
      (path === "/v1/chat/completions" || path === "/chat/completions")
    ) {
      return handleChatCompletions(request, env);
    }

    if (request.method === "GET" && (path === "/" || path === "/health")) {
      return json({
        ok: true,
        service: env.GATEWAY_NAME || "kaibau-gateway",
        endpoints: ["GET /v1/models", "POST /v1/chat/completions"],
      });
    }

    return json({ error: { message: `Not found: ${path}`, type: "invalid_request_error" } }, 404);
  },
};
