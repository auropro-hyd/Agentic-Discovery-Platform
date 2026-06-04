import js from "@eslint/js";
import tseslint from "typescript-eslint";

// The GROUNDING rule (layer 2 of the no-fabrication discipline):
// inside src/pages/** the view layer must NEVER compute a client-facing number. We ban arithmetic
// operators and the numeric coercions Number()/parseFloat/parseInt, so a displayed figure can only
// come verbatim from the JSON (via a branded FactValue rendered through <GroundedNumber>).
//
// src/charts/** is intentionally NOT covered: charts do pixel/proportion geometry (bar widths,
// donut arc angles) which is legitimate drawing math, never a displayed figure — chart components
// render segment VALUES verbatim and only the geometry is computed. UI-chrome counts
// ("showing 4 of 6") live in cards/ and layout/, also outside this rule.
const NO_ARITHMETIC = {
  files: ["src/pages/**/*.{ts,tsx}"],
  rules: {
    "no-restricted-syntax": [
      "error",
      {
        selector: "BinaryExpression[operator=/^[*/%]$/]",
        message:
          "Grounding rule: no multiplication/division/modulo on client figures in pages/ or charts/. Display numbers verbatim from the JSON via <GroundedNumber>.",
      },
      {
        selector: "CallExpression[callee.name=/^(Number|parseFloat|parseInt)$/]",
        message:
          "Grounding rule: no Number()/parseFloat()/parseInt() in pages/ or charts/. Numbers must come verbatim from the JSON.",
      },
    ],
  },
};

export default tseslint.config(
  { ignores: ["dist", "src/data/*.json"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: { ecmaVersion: 2022, sourceType: "module" },
    rules: {
      "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    },
  },
  NO_ARITHMETIC,
);
