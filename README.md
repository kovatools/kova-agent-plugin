<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://kovatools.com/brand/kova-lockup-horizontal.svg">
    <img src="https://kovatools.com/brand/kova-lockup-on-light.svg" alt="Kova" width="220">
  </picture>
</p>

# Give every agent the same investment strategy.

Kova is the strategy layer for agentic investors. It gives compatible AI agents a persistent investment strategy, a shared way to check portfolio alignment, and a clear approval boundary before Kova saves a strategy or creates a brief.

[Explore Kova](https://kovatools.com/agents) · [Install the Agent Plugin](#install)

## From strategy to brief

**Strategy → approval → portfolio → brief**

1. Turn your goals, constraints, and investing principles into a durable strategy.
2. Review the exact strategy and approve it before Kova saves anything.
3. Connect a portfolio, then ask an agent to check it against the same strategy.
4. Approve the portfolio check and receive a strategic brief with alignment, tensions, and next questions.

## What the plugin adds

- **Create or refine a strategy.** Shape a personal investment strategy in conversation, with a complete preview before it is saved.
- **Check portfolio alignment.** Use the strategy as the stable reference point for a portfolio review and strategic brief.

The plugin packages Kova's strategy workflows and secure MCP connection for clients that support [Agent Plugins v1](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md). It connects to Kova's hosted service, so there is no local server to build and no API key to place in a file.

## Trust and approval boundaries

Kova asks for explicit approval before it saves a strategy, records portfolio assets or liabilities, or creates a brief. It does not execute trades, make market predictions, or choose securities for you.

Authentication happens through Kova's OAuth flow. The plugin contains no credentials, authorization headers, tokens, or client-specific OAuth configuration. Strategy text, holdings, and account data stay out of the plugin package.

> The published Kova app in ChatGPT is a separate distribution channel. Installing that app does not install this Agent Plugin, and installing this Agent Plugin does not add the ChatGPT app.

## Install

The directory containing `plugin.json` is the plugin root. Install the repository root, not its `skills/` directory.

### VS Code: install directly from Git

VS Code can clone and install a plugin from its repository URL:

1. Make sure Agent Plugins are enabled with the `chat.plugins.enabled` setting.
2. Open the Command Palette and run **Chat: Install Plugin From Source**.
3. Enter `https://github.com/kovatools/kova-agent-plugin`.
4. Review the source trust prompt, install the plugin, and start a new chat.

To update, run **Extensions: Check for Extension Updates**. VS Code also checks automatically when extension auto-update is enabled. To uninstall, find Kova under **Agent Plugins - Installed**, open its context menu, and select **Uninstall**.

For a local clone instead, register the plugin root in VS Code settings:

```json
{
  "chat.pluginLocations": {
    "/absolute/path/to/kova-agent-plugin": true
  }
}
```

See [Agent plugins in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-plugins) for the current UI and settings.

### Cursor: clone or symlink locally

Cursor loads local plugins from `~/.cursor/plugins/local`:

```sh
mkdir -p ~/.cursor/plugins/local
git clone https://github.com/kovatools/kova-agent-plugin.git ~/.cursor/plugins/local/kova
```

Restart Cursor or run **Developer: Reload Window**. For development, you can clone elsewhere and symlink the repository root instead:

```sh
ln -s /absolute/path/to/kova-agent-plugin ~/.cursor/plugins/local/kova
```

To update a cloned copy, run `git -C ~/.cursor/plugins/local/kova pull --ff-only`, then reload Cursor. To uninstall, remove only the `kova` clone or symlink from `~/.cursor/plugins/local`, then reload Cursor. See [Cursor Plugins](https://cursor.com/docs/plugins) for the current local-plugin flow.

### Other compatible clients

Clone a release, then copy or symlink the repository root into the directory your client scans for plugins:

```sh
git clone --branch v0.1.1 --depth 1 https://github.com/kovatools/kova-agent-plugin.git
```

If Git is unavailable, download the `v0.1.1` source archive from GitHub, extract it, and register the extracted repository root as a local plugin directory.

Registration, update, and uninstall behavior belongs to the client because Agent Plugins v1 defines the package format, not a universal installer. Consult the [compatible clients list](https://agent-plugins.org/compatible-clients) and your client's documentation. To update a clone tracking `main`, use `git pull --ff-only`; for an immutable release, replace the clone with a newer SemVer tag. To uninstall, unregister the plugin root and remove only that local clone or symlink.

## Authenticate

The first time a client connects to `https://kovatools.com/mcp`, it should open Kova's OAuth authorization flow:

1. Sign in to your Kova account in the browser window.
2. Review the client name and requested access.
3. Select **Allow access**.
4. Return to the client and retry the request if it does not refresh automatically.

Kova uses OAuth with PKCE. Local clients may use an exact `http://localhost`, `http://127.0.0.1`, or `http://[::1]` callback. Cursor may also use its exact native callback, `cursor://anysphere.cursor-mcp/oauth/callback`; every other callback must use HTTPS. An active Kova subscription is required for MCP access.

To revoke a connection, remove its Kova API token from your account. Uninstalling the plugin does not revoke an already issued token.

## Releases and support

Use immutable [GitHub Releases](https://github.com/kovatools/kova-agent-plugin/releases) for repeatable installs and version-specific compatibility notes. To report an installation problem, client compatibility issue, or workflow bug, [open an issue](https://github.com/kovatools/kova-agent-plugin/issues).

## License

MIT
