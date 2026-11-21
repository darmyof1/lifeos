// Send log plugin entry (APR-0136). Hook-only and observe-only: it registers exactly two hooks, after_tool_call and message_received.
// The handlers return nothing (the host ignores return values). It never registers before_tool_call (that hook fails closed and could block a send),
// and no tool, command, service, route or other hook.
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createHandlers } from "./log.js";

export default definePluginEntry({
  id: "send-log",
  name: "Send log",
  description: "Observe-only send log (metadata only, no message text)",
  register(api) {
    const h = createHandlers({ logger: api.logger });
    api.on("after_tool_call", h.afterToolCall);
    api.on("message_received", h.messageReceived);
  },
});
