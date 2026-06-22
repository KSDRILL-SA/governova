/** Hover provider: hovering an S{C}.{N} reference shows the standard from the index. */
import * as vscode from "vscode";
import { Constitutions } from "./constitution";

export function registerHover(
  context: vscode.ExtensionContext,
  cons: Constitutions
): void {
  const provider: vscode.HoverProvider = {
    provideHover(document, position) {
      const range = document.getWordRangeAtPosition(position, /S\d+\.\d+/);
      if (!range) {
        return undefined;
      }
      const id = document.getText(range);
      const s = cons.standard(id);
      if (!s) {
        return undefined;
      }
      const md = new vscode.MarkdownString();
      md.isTrusted = true;
      md.appendMarkdown(`**${s.id} — ${s.title}**\n\n`);
      if (s.priority || s.phase_label) {
        md.appendMarkdown(`*${[s.priority, s.phase_label].filter(Boolean).join(" · ")}*\n\n`);
      }
      md.appendMarkdown(`${s.statement}\n\n`);
      if (s.anti_patterns?.length) {
        md.appendMarkdown(`**Anti-patterns**\n`);
        for (const ap of s.anti_patterns) {
          md.appendMarkdown(`- \`${ap.id}\` — ${ap.description}\n`);
        }
      }
      return new vscode.Hover(md, range);
    },
  };
  context.subscriptions.push(
    vscode.languages.registerHoverProvider({ scheme: "file" }, provider)
  );
}
