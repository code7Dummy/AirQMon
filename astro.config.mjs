import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://airquality.epa.ie",
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
});
