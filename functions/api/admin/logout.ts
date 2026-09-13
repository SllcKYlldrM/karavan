import { clearSessionCookie, json } from "./_lib";

export const onRequestPost = async () => json({ ok: true }, 200, { "set-cookie": clearSessionCookie, "cache-control": "no-store" });
