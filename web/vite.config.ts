import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            {
              name: "leaflet",
              test: /[\\/]node_modules[\\/](leaflet|react-leaflet)[\\/]/,
            },
            {
              name: "recharts",
              test: /[\\/]node_modules[\\/](recharts|react-is)[\\/]/,
            },
          ],
        },
      },
    },
  },
});