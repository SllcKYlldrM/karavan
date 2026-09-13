const encoder = new TextEncoder();
const SESSION_COOKIE = "vanspecs_admin_session";
const SESSION_TTL = 60 * 60 * 8;

type Env = {
  ADMIN_PASSWORD?: string;
  GITHUB_TOKEN?: string;
  GITHUB_OWNER?: string;
  GITHUB_REPO?: string;
  GITHUB_BRANCH?: string;
};

export const json = (body: unknown, status = 200, headers: HeadersInit = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...headers },
  });

const toBase64Url = (bytes: Uint8Array) =>
  btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

const fromBase64Url = (value: string) => {
  const padded = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  return Uint8Array.from(atob(padded), character => character.charCodeAt(0));
};

const sign = async (value: string, secret: string) => {
  const key = await crypto.subtle.importKey("raw", encoder.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
  return new Uint8Array(await crypto.subtle.sign("HMAC", key, encoder.encode(value)));
};

export const createSessionCookie = async (secret: string) => {
  const value = toBase64Url(encoder.encode(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + SESSION_TTL })));
  const signature = toBase64Url(await sign(value, secret));
  return SESSION_COOKIE + "=" + value + "." + signature + "; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=" + SESSION_TTL;
};

export const clearSessionCookie = SESSION_COOKIE + "=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0";

export const isAuthenticated = async (request: Request, env: Env) => {
  const secret = env.ADMIN_PASSWORD;
  if (!secret) return false;
  const cookie = request.headers.get("cookie")?.match(new RegExp(SESSION_COOKIE + "=([^;]+)"))?.[1];
  if (!cookie) return false;
  const parts = cookie.split(".");
  if (parts.length !== 2) return false;
  try {
    const payload = JSON.parse(new TextDecoder().decode(fromBase64Url(parts[0])));
    if (!payload.exp || payload.exp < Math.floor(Date.now() / 1000)) return false;
    const key = await crypto.subtle.importKey("raw", encoder.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["verify"]);
    return crypto.subtle.verify("HMAC", key, fromBase64Url(parts[1]), encoder.encode(parts[0]));
  } catch {
    return false;
  }
};

export const requireAuth = async (request: Request, env: Env) =>
  (await isAuthenticated(request, env)) ? null : json({ error: "Unauthorized" }, 401, { "cache-control": "no-store" });

export const githubConfig = (env: Env) => ({
  token: env.GITHUB_TOKEN,
  owner: env.GITHUB_OWNER || "SllcKYlldrM",
  repo: env.GITHUB_REPO || "karavan",
  branch: env.GITHUB_BRANCH || "main",
});

export const githubRequest = async (env: Env, path: string, init: RequestInit = {}) => {
  const config = githubConfig(env);
  if (!config.token) throw new Error("GITHUB_TOKEN is not configured");
  const response = await fetch("https://api.github.com" + path, {
    ...init,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: "Bearer " + config.token,
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "VanSpecs-Admin",
      ...(init.headers || {}),
    },
  });
  if (!response.ok) throw new Error("GitHub API " + response.status);
  return response;
};

export const configuredGithubPath = (env: Env, slug: string) => {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/i.test(slug)) throw new Error("Invalid post slug");
  const config = githubConfig(env);
  return "/repos/" + config.owner + "/" + config.repo + "/contents/src/content/posts/" + encodeURIComponent(slug) + ".md";
};

export const decodeContent = (content: string) => {
  const binary = atob(content.replace(/\n/g, ""));
  return new TextDecoder().decode(Uint8Array.from(binary, character => character.charCodeAt(0)));
};

export const encodeContent = (content: string) => {
  const bytes = encoder.encode(content);
  let binary = "";
  bytes.forEach(byte => { binary += String.fromCharCode(byte); });
  return btoa(binary);
};

const parseValue = (value: string) => {
  const trimmed = value.trim();
  if ((trimmed.startsWith("\"") && trimmed.endsWith("\"")) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) return trimmed.slice(1, -1);
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  return trimmed;
};

export const parsePost = (raw: string) => {
  const match = raw.match(/^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/);
  if (!match) throw new Error("Invalid frontmatter");
  const meta: Record<string, unknown> = {};
  const lines = match[1].split(/\r?\n/);
  for (let index = 0; index < lines.length; index += 1) {
    const field = lines[index].match(/^([A-Za-z][\w-]*):\s*(.*)$/);
    if (!field) continue;
    const key = field[1];
    if (key === "tags" && !field[2]) {
      const tags: string[] = [];
      while (index + 1 < lines.length && /^\s+-\s+/.test(lines[index + 1])) tags.push(String(parseValue(lines[++index].replace(/^\s+-\s+/, ""))));
      meta[key] = tags;
    } else {
      meta[key] = parseValue(field[2]);
    }
  }
  return { meta, body: match[2].trimStart() };
};

export const quote = (value: unknown) => JSON.stringify(String(value ?? ""));

export const serializePost = (meta: Record<string, unknown>, body: string) => {
  const order = ["author", "pubDatetime", "modDatetime", "title", "postSlug", "category", "featured", "draft", "tags", "ogImage", "description", "canonicalURL", "hideEditPost", "timezone"];
  const keys = [...order, ...Object.keys(meta).filter(key => !order.includes(key))];
  const lines: string[] = ["---"];
  keys.forEach(key => {
    const value = meta[key];
    if (value === undefined || value === null || value === "") return;
    if (key === "tags" && Array.isArray(value)) lines.push("tags", ...value.map(tag => "  - " + quote(tag)));
    else if (typeof value === "boolean") lines.push(key + ": " + value);
    else lines.push(key + ": " + quote(value));
  });
  lines.push("---", "", body.trim(), "");
  return lines.join("\n");
};
