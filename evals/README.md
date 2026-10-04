# Kova Agent Plugin evals

Runs with Claude Code's plugin eval runner. The Kova MCP server is mocked: `mocks/kova/_tools.json` is a saved `tools/list` from the live server, and the tool mocks return synthetic data, so no Kova account or network is needed.

```bash
claude plugin eval .                                   # all cases, with vs without the plugin
claude plugin eval . --case save-asks-first --runs 1 --ablation none
```

The cases check the approval boundaries in the two skills: reads stay read-only, and nothing is saved or evaluated without explicit approval.
