import { createSessionCookie, json } from "./_lib";

export const onRequestPost = async ({ request, env }: any) => {
  const password = env.ADMIN_PASSWORD;
  if (!password) return json({ error: "Admin password is not configured" }, 503);
  const input = await request.json().catch(() => ({}));
  if (typeof input.password !== "string" || input.password !== password) return json({ error: "Invalid password" }, 401);
  return json({ ok: true }, 200, { "set-cookie": await createSessionCookie(password), "cache-control": "no-store" });
};
