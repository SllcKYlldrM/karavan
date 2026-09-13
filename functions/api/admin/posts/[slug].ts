import { configuredGithubPath, decodeContent, encodeContent, githubConfig, githubRequest, json, parsePost, requireAuth, serializePost } from "../_lib";

const getFile = async (env: any, slug: string) => {
  const config = githubConfig(env);
  const response = await githubRequest(env, configuredGithubPath(env, slug) + "?ref=" + encodeURIComponent(config.branch));
  const file = await response.json() as any;
  return { config, file, parsed: parsePost(decodeContent(file.content)) };
};

export const onRequestPut = async ({ request, env, params }: any) => {
  const unauthorized = await requireAuth(request, env);
  if (unauthorized) return unauthorized;
  try {
    const payload = await request.json();
    const current = await getFile(env, params.slug);
    const meta = {
      ...current.parsed.meta,
      title: String(payload.title || current.parsed.meta.title || ""),
      author: String(payload.author || current.parsed.meta.author || ""),
      category: String(payload.category || current.parsed.meta.category || ""),
      tags: Array.isArray(payload.tags) ? payload.tags.map(String) : current.parsed.meta.tags,
      description: String(payload.description || current.parsed.meta.description || ""),
    };
    const content = serializePost(meta, String(payload.body || ""));
    const response = await githubRequest(env, configuredGithubPath(env, params.slug), {
      method: "PUT",
      body: JSON.stringify({ message: "content: update " + params.slug, content: encodeContent(content), sha: current.file.sha, branch: current.config.branch }),
      headers: { "content-type": "application/json" },
    });
    return json({ ok: true, commit: (await response.json() as any).commit?.sha });
  } catch (error) {
    return json({ error: error instanceof Error ? error.message : "Unable to update post" }, 500);
  }
};

export const onRequestDelete = async ({ request, env, params }: any) => {
  const unauthorized = await requireAuth(request, env);
  if (unauthorized) return unauthorized;
  try {
    const current = await getFile(env, params.slug);
    const response = await githubRequest(env, configuredGithubPath(env, params.slug), {
      method: "DELETE",
      body: JSON.stringify({ message: "content: delete " + params.slug, sha: current.file.sha, branch: current.config.branch }),
      headers: { "content-type": "application/json" },
    });
    return json({ ok: true, commit: (await response.json() as any).commit?.sha });
  } catch (error) {
    return json({ error: error instanceof Error ? error.message : "Unable to delete post" }, 500);
  }
};
