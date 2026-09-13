import { configuredGithubPath, decodeContent, githubConfig, githubRequest, json, parsePost, requireAuth } from "./_lib";

export const onRequestGet = async ({ request, env }: any) => {
  const unauthorized = await requireAuth(request, env);
  if (unauthorized) return unauthorized;
  try {
    const config = githubConfig(env);
    const response = await githubRequest(env, "/repos/" + config.owner + "/" + config.repo + "/contents/src/content/posts?ref=" + encodeURIComponent(config.branch));
    const files = (await response.json() as any[]).filter(file => file.type === "file" && file.name.endsWith(".md"));
    const posts = await Promise.all(files.map(async file => {
      const slugFromFile = file.name.replace(/\.md$/, "");
      const contentResponse = await githubRequest(env, configuredGithubPath(env, slugFromFile) + "?ref=" + encodeURIComponent(config.branch));
      const raw = decodeContent((await contentResponse.json() as any).content);
      const parsed = parsePost(raw);
      const slug = String(parsed.meta.postSlug || slugFromFile);
      return {
        slug,
        file: file.name,
        title: parsed.meta.title || slug,
        author: parsed.meta.author || "",
        category: parsed.meta.category || (Array.isArray(parsed.meta.tags) ? parsed.meta.tags[0] : "Uncategorized"),
        tags: parsed.meta.tags || [],
        description: parsed.meta.description || "",
        pubDatetime: parsed.meta.pubDatetime || "",
        body: parsed.body,
      };
    }));
    return json(posts, 200, { "cache-control": "no-store" });
  } catch (error) {
    return json({ error: error instanceof Error ? error.message : "Unable to load posts" }, 500);
  }
};
