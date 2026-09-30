import react from '@vitejs/plugin-react'
import checker from 'vite-plugin-checker'
import { defineConfig } from 'vite'
import path from "node:path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    checker({
      typescript: {
        tsconfigPath: "./tsconfig.app.json",
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "src"),
    },
  },
})
