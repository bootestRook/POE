import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const outDir = process.env.VITE_OUT_DIR || "dist";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    hmr: {
      host: "127.0.0.1",
      clientPort: 5173
    },
    proxy: {
      "/api": "http://127.0.0.1:8000"
    }
  },
  build: {
    outDir,
    emptyOutDir: true
  }
});
