import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const postsRoot = join(process.cwd(), "dist", "posts");

if (!existsSync(postsRoot)) {
  throw new Error("Post build output not found: dist/posts");
}

const failures = [];
const postDirectories = readdirSync(postsRoot, { withFileTypes: true })
  .filter(entry => entry.isDirectory())
  .filter(entry => !/^\d+$/.test(entry.name))
  .map(entry => entry.name);

for (const postDirectory of postDirectories) {
  const filePath = join(postsRoot, postDirectory, "index.html");
  if (!existsSync(filePath)) continue;

  const html = readFileSync(filePath, "utf8");
  const headingIds = new Set(
    [...html.matchAll(/<h[23][^>]*\sid="([^"]+)"/g)].map(match => match[1])
  );
  const tocLinks = [
    ...html.matchAll(/href="#([^"]+)"[^>]*data-toc-level="2"|data-toc-level="2"[^>]*href="#([^"]+)"/g),
  ].map(match => match[1] ?? match[2]);

  if (!html.includes('class="app-prose post-content')) {
    failures.push(`${postDirectory}: missing .post-content article container`);
  }

  for (const target of tocLinks) {
    if (!headingIds.has(target)) {
      failures.push(`${postDirectory}: TOC target #${target} does not resolve to an H2/H3`);
    }
  }

  if (tocLinks.length > 0) {
    if (!html.includes('class="contents lg:hidden"')) {
      failures.push(`${postDirectory}: mobile TOC must use a boxless wrapper so sticky can span the article`);
    }
    if (!html.includes('class="sticky top-20 z-30 mb-6')) {
      failures.push(`${postDirectory}: mobile TOC must remain sticky below the mobile header`);
    }
  }
}

if (failures.length > 0) {
  process.stderr.write("Post layout validation failed:\n");
  process.stderr.write(failures.map(failure => `- ${failure}`).join("\n") + "\n");
  process.exit(1);
}

process.stdout.write(`Post layout validation passed for ${postDirectories.length} post page(s).\n`);
