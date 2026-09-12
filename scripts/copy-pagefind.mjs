import { cpSync, existsSync, mkdirSync } from "node:fs";

const source = "dist/pagefind";
const target = "public/pagefind";

if (!existsSync(source)) {
  throw new Error(`Pagefind çıktısı bulunamadı: ${source}`);
}

mkdirSync("public", { recursive: true });
cpSync(source, target, { recursive: true });
