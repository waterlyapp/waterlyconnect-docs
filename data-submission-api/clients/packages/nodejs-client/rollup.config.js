import typescript from "rollup-plugin-typescript2";
import pkg from "./package.json";
import { dirname } from "path";

export default {
  input: "src/index.ts",
  external: ["axios"],
  plugins: [typescript({ tsconfig: "./tsconfig.json" })],
  output: [
    {
      dir: dirname(pkg.main),
      entryFileNames: "[name].js",
      format: "cjs",
      preserveModules: true,
    },
    {
      dir: dirname(pkg.module),
      entryFileNames: "[name].mjs",
      format: "esm",
      preserveModules: true,
    },
  ],
};
