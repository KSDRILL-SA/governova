/**
 * Reliable-tier (deterministic) violation detection.
 *
 * Per GOVERNOVA-STRATEGY §9 / §11.2, the IDE surface is *advisory, never blocking*:
 * these are Information/Warning diagnostics that show and explain, but never stop the
 * developer. Only deterministic, low-false-positive patterns live here; semantic
 * detection is reserved for the CI/PR surfaces.
 */
import * as vscode from "vscode";
import { Constitutions } from "./constitution";

interface Rule {
  /** Anti-pattern id, used as the diagnostic code and linked to the index. */
  code: string;
  /** Standard the anti-pattern violates. */
  standard: string;
  /** Languages this rule applies to (empty = all). */
  languages: string[];
  test: RegExp;
  message: string;
  severity: vscode.DiagnosticSeverity;
}

const RULES: Rule[] = [
  {
    code: "AP-S3.14a",
    standard: "S3.14",
    languages: ["typescript", "javascript", "typescriptreact", "javascriptreact"],
    test: /\b(?:local|session)Storage\.setItem\s*\(\s*['"`][^'"`]*(?:token|jwt|access|refresh|auth)[^'"`]*['"`]/i,
    message:
      "Auth token stored in web storage. Per S3.14, the access token belongs in memory and the refresh token in an HttpOnly cookie — localStorage/sessionStorage is XSS-exposed.",
    severity: vscode.DiagnosticSeverity.Warning,
  },
  {
    code: "AP-S2.17a",
    standard: "S2.17",
    languages: [],
    test: /(?:setAllowedOrigins\s*\(\s*[^)]*['"`]\*['"`]|Access-Control-Allow-Origin['"`]?\s*[:,]\s*['"`]\*['"`]|origin\s*:\s*['"`]\*['"`])/i,
    message:
      "Wildcard CORS origin. Per S2.17, allowed origins are configured explicitly per environment — never '*' in production.",
    severity: vscode.DiagnosticSeverity.Warning,
  },
  {
    code: "AP-S2.34a",
    standard: "S2.34",
    languages: ["java", "kotlin"],
    test: /\b(?:double|float)\s+\w*(?:price|amount|balance|total|cost|fee|money|currency)\w*/i,
    message:
      "Monetary value typed as double/float. Per S2.34 (and C6 financial precision), money uses BigDecimal — float arithmetic corrupts balances.",
    severity: vscode.DiagnosticSeverity.Warning,
  },
  {
    code: "AP-S2.18a",
    standard: "S2.18",
    languages: ["typescript", "javascript", "java", "python"],
    test: /\b(?:res\.(?:send|json)|return)\b[^;\n]*\b(?:e|err|error|ex)\.(?:stack|message|getMessage\(\))/,
    message:
      "Internal error detail returned to the client. Per S2.18, API errors never expose stack traces or internal messages — map to a generic, uniform error shape.",
    severity: vscode.DiagnosticSeverity.Information,
  },
];

export function registerDiagnostics(
  context: vscode.ExtensionContext,
  cons: Constitutions
): vscode.DiagnosticCollection {
  const collection = vscode.languages.createDiagnosticCollection("governova");
  context.subscriptions.push(collection);

  const run = (doc: vscode.TextDocument) => {
    if (!vscode.workspace.getConfiguration("governova").get<boolean>("diagnostics.enabled", true)) {
      collection.delete(doc.uri);
      return;
    }
    if (doc.uri.scheme !== "file") {
      return;
    }
    const diags: vscode.Diagnostic[] = [];
    const lines = doc.getText().split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      for (const rule of RULES) {
        if (rule.languages.length && !rule.languages.includes(doc.languageId)) {
          continue;
        }
        const m = rule.test.exec(line);
        if (!m) {
          continue;
        }
        const start = m.index;
        const range = new vscode.Range(i, start, i, start + m[0].length);
        const d = new vscode.Diagnostic(range, rule.message, rule.severity);
        d.source = "Governova";
        d.code = cons.standard(rule.standard)
          ? { value: rule.code, target: vscode.Uri.parse("command:governova.openStandard") }
          : rule.code;
        diags.push(d);
      }
    }
    collection.set(doc.uri, diags);
  };

  if (vscode.window.activeTextEditor) {
    run(vscode.window.activeTextEditor.document);
  }
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(run),
    vscode.workspace.onDidChangeTextDocument((e) => run(e.document)),
    vscode.workspace.onDidCloseTextDocument((doc) => collection.delete(doc.uri))
  );

  return collection;
}
