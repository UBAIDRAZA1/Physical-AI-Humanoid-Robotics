---
id: 3
title: Fix 'process is not defined' error in Chatbot component
stage: misc
date: 2025-12-10
surface: agent
model: claude-3-opus
feature: ai-textbook-platform
branch: main
user: Administrator
command: "Fix 'process is not defined' error"
labels: ["bug-fix", "docusaurus", "environment-variables"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - physical-ai-book/docusaurus.config.ts
  - physical-ai-book/src/components/Chatbot/Chatbot.tsx
tests_yaml: []
prompt_text: |
  Uncaught runtime errors:
  ×
  ERROR
  process is not defined
  ReferenceError: process is not defined
      at eval (webpack-internal:///./src/components/Chatbot/Chatbot.tsx:9:24)
      at ./src/components/Chatbot/Chatbot.tsx (http://localhost:3000/physical-ai-book/__comp---site-src-pages-index-tsx-1-df-d3e.js:22:1)
      at __webpack_require__ (http://localhost:3000/physical-ai-book/runtime~main.js:34:32)
      at fn (http://localhost:3000/physical-ai-book/runtime~main.js:321:21)
      at eval (webpack-internal:///./src/pages/index.tsx:10:94)
      at ./src/pages/index.tsx (http://localhost:3000/physical-ai-book/__comp---site-src-pages-index-tsx-1-df-d3e.js:50:1)
      at __webpack_require__ (http://localhost:3000/physical-ai-book/runtime~main.js:34:32)
      at fn (http://localhost:3000/physical-ai-book/runtime~main.js:321:21)
response_text: |
  The error `process is not defined` in `Chatbot.tsx` indicates that Node.js-specific code was being executed in a browser environment.

  **Plan:**
  1.  **Read `physical-ai-book/src/components/Chatbot/Chatbot.tsx`**: Identify the usage of `process.env`.
  2.  **Read `physical-ai-book/docusaurus.config.ts`**: Determine how to expose environment variables in a Docusaurus-compatible way.
  3.  **Modify `docusaurus.config.ts`**: Add `apiBaseUrl` to `customFields`.
  4.  **Modify `Chatbot.tsx`**: Update the component to use `useDocusaurusContext` to retrieve `apiBaseUrl` from `siteConfig.customFields`.

  **Outcome:**
  The `process.env` calls in `Chatbot.tsx` have been replaced with a Docusaurus-idiomatic approach using `customFields` from `docusaurus.config.ts`. This resolves the runtime error by providing a client-side accessible configuration value.
---
## Description

The user reported a runtime error "process is not defined" originating from `physical-ai-book/src/components/Chatbot/Chatbot.tsx`. This error typically occurs when Node.js-specific global objects (`process`) are accessed in a client-side (browser) environment.

Upon investigation, it was found that the `Chatbot.tsx` component was attempting to read API base URLs from `process.env.REACT_APP_API_URL` or `process.env.NEXT_PUBLIC_API_URL`. In a Docusaurus environment, client-side accessible environment variables or configuration should be managed differently.

The fix involved:
1.  Adding a `customFields` object to `physical-ai-book/docusaurus.config.ts` to expose an `apiBaseUrl` (defaulting to `http://localhost:8000`) to the client.
2.  Modifying `physical-ai-book/src/components/Chatbot/Chatbot.tsx` to import and utilize the `useDocusaurusContext` hook. This hook provides access to the Docusaurus site configuration, including the newly defined `customFields.apiBaseUrl`.
3.  Replacing the direct `process.env` access with the value retrieved from `siteConfig.customFields.apiBaseUrl`.

This change ensures that the Chatbot component correctly retrieves its API base URL in a Docusaurus-compatible manner, eliminating the `process is not defined` runtime error.