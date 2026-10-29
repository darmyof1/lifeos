// CEO ledger plugin entry (APR-0102). Hook-only and observe-only: it registers exactly one hook, message_received, whose type returns
// nothing (the host ignores return values and runs the handler fire-and-forget), and no tool, command, service, route or other hook.
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createHandler } from "./ledger.js";

export default definePluginEntry({
  id: "ceo-ledger",
  name: "CEO ledger",
  description: "Observe-only CEO message ledger for the delete gate",
  register(api) {
    const handler = createHandler({ logger: api.logger });
    api.on("message_received", handler);
  },
});
