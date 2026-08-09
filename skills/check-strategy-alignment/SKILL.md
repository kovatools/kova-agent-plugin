---
name: check-strategy-alignment
description: Check how a portfolio aligns with a saved Kova investment strategy and summarize the resulting brief. Use when the user asks for an alignment score, portfolio review, compliance check, or updated Kova brief.
---

# Check Kova strategy alignment

Read existing Kova data freely, but obtain explicit approval before starting a new evaluation. A new evaluation can update the portfolio on file and creates a persisted brief.

## Resolve the strategy and request

Use `kova_list_strategies` when needed and retain the exact strategy UUID. Call `kova_show_strategy` to confirm the selected strategy.

Determine whether the user wants:

- the latest existing brief, which is read-only; or
- a new evaluation using current, supplied, or already saved portfolio data.

For the latest existing brief, call `kova_show_brief` with `brief_id` set to `latest` and summarize it. Do not start a new evaluation unless the user asks for one.

## Prepare a new evaluation

Establish the portfolio source. Call `kova_show_portfolio` if the user wants the current Kova portfolio. Use a connected account or attached file only when it is actually available. If no source is available, ask the user to paste, upload, or describe the holdings.

Call `kova_show_portfolio` before proposing changes so you can identify existing regular holdings, manual assets, and liabilities. If that exact confirmed strategy returns `No portfolio found for this strategy`, treat it as an empty existing portfolio and continue classifying the supplied holdings. Report any other lookup failure and stop without writes or evaluation.

Establish whether supplied holdings are a complete replacement for the strategy's full current holdings and debt scope or a partial update. Clarify the scope if it is ambiguous. Do not send a raw mixed list to `kova_evaluate_portfolio`. Classify every supplied item first:

- **Regular portfolio:** only clearly identified US-listed stocks, US-listed ETFs, and USD cash. Preserve confirmed tickers and quantities. Never silently correct a symbol. For example, ask whether `APPL` was intended to mean `AAPL`.
- **Manual assets:** use `real_estate` for property, `bitcoin` for direct Bitcoin, `investment_account` for a managed account known only by total value, and `other` for another non-ticker asset. Property, managed accounts, and `other` require a current total value in USD. Direct Bitcoin requires quantity and uses live pricing. Preserve a useful name and any user-provided description in `notes`.
- **Liabilities:** use liability tools only for explicitly stated mortgages, loans, lines of credit, or other debts. Never infer debt from ownership of an asset.
- **Needs clarification or unsupported:** clarify an ambiguous ticker, quantity, instrument type, listing, or value. Options, non-US securities, funds that are not US-listed ETFs, and cryptocurrencies other than direct Bitcoin are outside this guided portfolio format. Offer `other` only when the user supplies a current USD value and explicitly accepts that instrument-level detail will not be preserved. Otherwise omit the item and disclose that omission.

Before building the regular portfolio representation, partition `holdings.assets` returned by `kova_show_portfolio`: an entry with a UUID is a registered manual asset, while an entry without a UUID is part of the saved normalized snapshot. Never copy a UUID-bearing registered asset into portfolio JSON. Treat every UUID-less snapshot asset as part of the replaceable saved snapshot even when its type resembles a manually routed asset.

Build the regular portfolio representation according to the confirmed scope. For a partial update that changes any regular holding or cash, start from the saved regular portfolio returned by `kova_show_portfolio` and apply only the confirmed changes. Preserve every unmatched saved stock or ETF, preserve existing options unchanged, preserve every unmatched UUID-less snapshot asset unchanged in the schema-valid `assets` array, and preserve the exact saved cash balance unless the user explicitly changes it. Never infer a position or snapshot-asset removal or zero cash from omission. If a partial update changes only manual assets or liabilities and a saved regular snapshot exists, omit `portfolio` only after previewing and explicitly confirming that Kova will reuse that complete saved regular snapshot.

For a complete replacement, require confirmation that the supplied set is complete. Preview every saved stock, ETF, or option that will disappear and the old cash balance that will be replaced. Require an explicit cash value or explicit zero. Do not remove an unsupported saved option from silence; clarify whether to retain or remove it. For every UUID-less saved snapshot asset, require an explicit choice to retain it unchanged in `assets`, migrate it to a registered manual asset, or remove it in the replacement. Never silently match a supplied item to a snapshot asset. Migration requires the separate asset-write preview and approval; create the correctly routed manual record first, and omit the old snapshot entry only after that write succeeds so the evaluation cannot duplicate or lose it. Never put UUID-bearing registered assets or liabilities in the regular portfolio JSON.

Whenever you supply `portfolio`, serialize the exact final full regular state as schema-valid portfolio v1 JSON with `schema_version`, `stocks`, `options`, `cash`, a current UTC `timestamp`, `notes`, and `assets` whenever a UUID-less snapshot asset is retained. Pass that serialized JSON as the string-valued argument. Do not send free text or rely on normalization to preserve positions.

Show a grouped preview with the headings **Regular portfolio**, **Assets and liabilities**, and **Needs clarification or unsupported**. Resolve every item in the last group before seeking approval. Match manual records against `kova_show_portfolio`; update an existing record using its exact UUID instead of creating a duplicate. For a complete replacement, compare every persisted manual record with the confirmed input. Preview each unmatched record by name and exact UUID as a proposed `kova_remove_asset` or `kova_remove_liability` call, but never infer from omission alone that an asset was sold or a debt was repaid. For a partial update, retain unmatched records and disclose that they remain included in the evaluation. Show the exact asset and liability creates, updates, or removals and obtain explicit approval before those writes. Approval for them is not approval for an evaluation.

After approved asset and liability changes complete, call `kova_show_portfolio` again and show the combined current state. Request separate approval for `kova_evaluate_portfolio`. Pass only the complete regular portfolio representation because registered assets and liabilities are included automatically. If the user confirms there are no US stock, ETF, or cash holdings in scope and no saved option or UUID-less snapshot asset is being retained, set the string-valued `portfolio` argument to a serialized, schema-complete JSON document: `"{\"schema_version\":\"1.0.0\",\"stocks\":[],\"options\":[],\"cash\":0,\"timestamp\":\"<current UTC as YYYY-MM-DDTHH:MM:SSZ>\",\"notes\":[]}"`. If a saved option or UUID-less snapshot asset is being retained, include it in the schema-complete `options` or `assets` array even when `stocks` is empty and `cash` is zero. Replace the timestamp placeholder before the call. Do not pass an object at the tool-argument level, and do not omit the portfolio argument and accidentally reuse stale regular holdings.

Before calling `kova_evaluate_portfolio`, show:

- the exact strategy name and UUID;
- the portfolio source;
- the exact final full regular state and its additions, changes, and removals;
- whether Kova will reuse the saved portfolio or replace it with supplied portfolio text; and
- any context that will be included.

Explain that the evaluation creates a persisted brief and that supplied portfolio data becomes the portfolio on file. Ask the user to approve this exact evaluation. Do not infer approval from a request to inspect or prepare the inputs. If any input changes, ask again.

## Evaluate and report

After approval, call `kova_evaluate_portfolio` with the exact strategy UUID. Retain the returned `brief_id`. Poll `kova_show_brief` using that UUID and ID, waiting at least the returned `retry_after_seconds` between calls. Stop polling and report the error if the brief fails.

When complete, summarize:

- the alignment score and label;
- the top two or three observations;
- the first tactical move described by the brief; and
- the Kova URL from the result.

Clearly distinguish Kova's analysis from an instruction to trade.

## Guardrails

- Never evaluate a different strategy because its display name looks similar. Use the exact UUID.
- Do not execute trades, place orders, predict markets, or promise returns.
- Do not silently substitute hypothetical holdings for the user's current portfolio.
- Keep account data and credentials out of logs, screenshots, cassettes, and files.
- If the user only wants a hypothetical comparison, explain that this guided workflow handles current holdings and do not persist the hypothetical portfolio.
