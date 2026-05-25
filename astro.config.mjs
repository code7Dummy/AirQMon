import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  site: "https://airqmon.code7dummy.workers.dev",
  integrations: [],

  vite: {
    plugins: [tailwindcss()],

  },

  build: {
    format: "directory",
  },

  devToolbar: {
    enabled: false,
  },

  server: {
    port: 4321,
  },

  adapter: cloudflare(),
});