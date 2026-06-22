/**
 * Governova IDE extension — the wedge.
 *
 * Consumes the compiled constitutional index (compiled/constitution.json, produced
 * by `governova-compile`) and surfaces it in the editor: a Standards explorer, hover
 * docs for any S{C}.{N} reference, reliable-tier (advisory) violation diagnostics, and
 * a `.cursorrules` generator so the AI you build with inherits the governance.
 */
import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { Constitutions } from "./constitution";
import { StandardsTreeProvider } from "./tree";
import { registerHover } from "./hover";
import { registerDiagnostics } from "./diagnostics";

export function activate(context: vscode.ExtensionContext): void {
  const cons = new Constitutions();
  const loaded = cons.load();

  const tree = new StandardsTreeProvider(cons);
  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("governovaStandards", tree)
  );

  registerHover(context, cons);
  registerDiagnostics(context, cons);

  const reload = () => {
    const ok = cons.load();
    tree.refresh();
    if (ok) {
      vscode.window.setStatusBarMessage(
        `Governova: ${cons.standardCount} standards loaded`,
        4000
      );
    } else {
      vscode.window.showWarningMessage(
        "Governova: compiled/constitution.json not found. Run `governova-compile`, or set governova.indexPath."
      );
    }
    return ok;
  };

  context.subscriptions.push(
    vscode.commands.registerCommand("governova.refresh", reload),

    vscode.commands.registerCommand("governova.openStandard", async (id?: string) => {
      if (!id) {
        return;
      }
      const s = cons.standard(id);
      if (!s) {
        vscode.window.showInformationMessage(`Governova: ${id} not found in the index.`);
        return;
      }
      const lines = [
        `# ${s.id} — ${s.title}`,
        "",
        [s.priority, s.phase_label, s.applies_to].filter(Boolean).join(" · "),
        "",
        "## Standard",
        s.statement,
      ];
      if (s.rationale) {
        lines.push("", "## Rationale", s.rationale);
      }
      if (s.anti_patterns?.length) {
        lines.push("", "## Anti-patterns");
        for (const ap of s.anti_patterns) {
          lines.push(`- \`${ap.id}\` — ${ap.description}`);
        }
      }
      const doc = await vscode.workspace.openTextDocument({
        content: lines.join("\n"),
        language: "markdown",
      });
      await vscode.window.showTextDocument(doc, { preview: true });
    }),

    vscode.commands.registerCommand("governova.showStandard", async () => {
      if (!cons.loaded) {
        reload();
      }
      const picks = cons.allStandards().map((s) => ({
        label: s.id,
        description: s.title,
        detail: s.statement.slice(0, 160),
        id: s.id,
      }));
      const choice = await vscode.window.showQuickPick(picks, {
        placeHolder: `Find a standard (${cons.standardCount} loaded)`,
        matchOnDescription: true,
        matchOnDetail: true,
      });
      if (choice) {
        vscode.commands.executeCommand("governova.openStandard", choice.id);
      }
    }),

    vscode.commands.registerCommand("governova.generateCursorrules", async () => {
      if (!cons.loaded && !reload()) {
        return;
      }
      const folder = vscode.workspace.workspaceFolders?.[0];
      if (!folder) {
        vscode.window.showWarningMessage("Governova: open a workspace first.");
        return;
      }
      const target = path.join(folder.uri.fsPath, ".cursorrules");
      fs.writeFileSync(target, buildCursorrules(cons), "utf-8");
      const doc = await vscode.workspace.openTextDocument(target);
      await vscode.window.showTextDocument(doc);
      vscode.window.showInformationMessage(
        `Governova: .cursorrules generated from ${cons.standardCount} standards.`
      );
    })
  );

  if (loaded) {
    vscode.window.setStatusBarMessage(
      `Governova: ${cons.standardCount} standards loaded`,
      4000
    );
  }
}

export function deactivate(): void {
  /* no-op */
}

function buildCursorrules(cons: Constitutions): string {
  const out: string[] = [
    "# Governova — AI development governance (generated)",
    `# Source: compiled/constitution.json — ${cons.standardCount} standards`,
    "",
    "You are building under the Governova constitutional framework. Follow these rules:",
    "",
    "## Hard rules",
    "- Cite the standard ID (S{C}.{N}) for every technical recommendation.",
    "- No AI references anywhere in commits, PRs, branches, or co-authors (S1.100). Human attribution only.",
    "- Branch -> issue -> PR -> merge, with full issue/PR metadata (S1.99).",
    "- AI may propose, recommend, and implement, but NEVER approves its own output for production (L4 is human-only).",
    "- Flag any constitutional violation; never silently comply.",
    "",
    "## Standards (id — title)",
  ];
  for (const c of cons.constitutions) {
    if (!c.standards.length) {
      continue;
    }
    out.push("", `### ${c.id} — ${c.name} (${c.standards.length})`);
    for (const s of c.standards) {
      out.push(`- ${s.id} — ${s.title}`);
    }
  }
  return out.join("\n") + "\n";
}
