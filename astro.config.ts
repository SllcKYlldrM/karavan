import {
  defineConfig,
  envField,
  fontProviders,
  svgoOptimizer,
} from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import { unified } from "@astrojs/markdown-remark";
import remarkToc from "remark-toc";
import remarkCollapse from "remark-collapse";
import rehypeCallouts from "rehype-callouts";
import {
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerNotationWordHighlight,
} from "@shikijs/transformers";
import { transformerFileName } from "./src/utils/transformers/fileName";
import fs from "node:fs";
import path from "node:path";
import { contentScopes } from "./src/data/category-tree";
import { slugifyStr } from "./src/utils/slugify";
import config from "./astro-paper.config";

const postsDirectory = path.resolve("src/content/posts");
const publishedPosts = fs
  .readdirSync(postsDirectory)
  .filter(fileName => /\.(md|mdx)$/.test(fileName))
  .map(fileName => fs.readFileSync(path.join(postsDirectory, fileName), "utf8"))
  .filter(content => !/^draft:\s*true\s*$/m.test(content))
  .map(content => {
    const scope = /^scope:\s*["']?([^"'\n]+)["']?\s*$/m.exec(content)?.[1]?.trim() ?? "caravan";
    const subcategory = /^subcategory:\s*["']?([^"'\n]+)["']?\s*$/m.exec(content)?.[1]?.trim() ?? "";
    const tagsBlock = /^tags:\s*\n((?:\s+-\s+.*\n?)*)/m.exec(content)?.[1] ?? "";
    const tags = [...tagsBlock.matchAll(/^\s+-\s+["']?([^"'\n]+)["']?\s*$/gm)].map(match => match[1].trim());
    return { scope, subcategory, tags };
  });

const sitemapExcludedPaths = new Set<string>();
for (const scope of contentScopes) {
  const scopePosts = publishedPosts.filter(post => post.scope === scope.id);
  if (scopePosts.length === 0) sitemapExcludedPaths.add(`/scopes/${scope.slug}/`);
  for (const group of scope.groups) {
    for (const child of group.children) {
      const hasPosts = scopePosts.some(post => post.subcategory === child);
      if (!hasPosts) sitemapExcludedPaths.add(`/scopes/${scope.slug}/${slugifyStr(child)}/`);
    }
  }
}

const tagCounts = new Map<string, number>();
for (const post of publishedPosts) {
  for (const tag of post.tags) tagCounts.set(slugifyStr(tag), (tagCounts.get(slugifyStr(tag)) ?? 0) + 1);
}
for (const [tag, count] of tagCounts) {
  if (count < 2) sitemapExcludedPaths.add(`/tags/${tag}/`);
}

export default defineConfig({
  site: config.site.url,
  integrations: [
    mdx(),
    sitemap({
      filter: page => {
        const pathname = new URL(page).pathname;
        return (
          (config.features?.showArchives !== false || !pathname.endsWith("/archives/")) &&
          !sitemapExcludedPaths.has(pathname)
        );
      },
    }),
  ],
  i18n: {
    locales: ["en"],
    defaultLocale: "en",
    routing: {
      prefixDefaultLocale: false,
    },
  },
  markdown: {
    processor: unified({
      remarkPlugins: [
        remarkToc,
        [remarkCollapse, { test: "Table of contents" }],
      ],
      rehypePlugins: [rehypeCallouts],
    }),
    shikiConfig: {
      themes: { light: "min-light", dark: "night-owl" },
      defaultColor: false,
      wrap: false,
      transformers: [
        transformerFileName({ style: "v2", hideDot: false }),
        transformerNotationHighlight(),
        transformerNotationWordHighlight(),
        transformerNotationDiff({ matchAlgorithm: "v3" }),
      ],
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
  fonts: [
    {
      name: "Google Sans Code",
      cssVariable: "--font-google-sans-code",
      provider: fontProviders.google(),
      fallbacks: ["monospace"],
      weights: [300, 400, 500, 600, 700],
      styles: ["normal", "italic"],
      formats: ["woff", "ttf"],
    },
  ],
  env: {
    schema: {
      PUBLIC_GOOGLE_SITE_VERIFICATION: envField.string({
        access: "public",
        context: "client",
        optional: true,
      }),
    },
  },
  experimental: {
    svgOptimizer: svgoOptimizer(),
  },
});
