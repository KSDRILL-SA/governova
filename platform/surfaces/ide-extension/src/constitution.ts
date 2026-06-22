/**
 * Loads the compiled Governova constitutional index (compiled/constitution.json,
 * produced by `governova-compile`) and exposes typed lookups.
 *
 * Only the fields the extension uses are typed here; the compiled index is the
 * single source of truth, so the extension never re-parses markdown.
 */
import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

export interface AntiPattern {
  id: string;
  description: string;
  parent_standard_id: string;
}

export interface Standard {
  id: string;
  title: string;
  constitution_id: string;
  priority?: string;
  applies_to?: string;
  phase?: string | null;
  phase_label?: string | null;
  statement: string;
  rationale?: string;
  anti_patterns: AntiPattern[];
  source_path?: string;
  source_line?: number;
}

export interface Constitution {
  id: string;
  number: number;
  name: string;
  phase?: string | null;
  standards: Standard[];
}

export interface CompiledIndex {
  compiled_at?: string;
  source_commit_sha?: string | null;
  constitutions: Constitution[];
}

const STANDARD_RE = /\bS\d+\.\d+\b/;

export class Constitutions {
  private index: CompiledIndex | undefined;
  private byId = new Map<string, Standard>();
  private apById = new Map<string, AntiPattern>();
  public indexPath: string | undefined;

  /** (Re)load the compiled index. Returns true on success. */
  load(): boolean {
    const p = this.resolveIndexPath();
    if (!p || !fs.existsSync(p)) {
      this.index = undefined;
      this.indexPath = undefined;
      return false;
    }
    try {
      const raw = fs.readFileSync(p, "utf-8");
      this.index = JSON.parse(raw) as CompiledIndex;
      this.indexPath = p;
      this.byId.clear();
      this.apById.clear();
      for (const c of this.index.constitutions) {
        for (const s of c.standards) {
          this.byId.set(s.id, s);
          for (const ap of s.anti_patterns ?? []) {
            this.apById.set(ap.id, ap);
          }
        }
      }
      return true;
    } catch {
      this.index = undefined;
      return false;
    }
  }

  get loaded(): boolean {
    return this.index !== undefined;
  }

  get constitutions(): Constitution[] {
    return this.index?.constitutions ?? [];
  }

  get standardCount(): number {
    return this.byId.size;
  }

  standard(id: string): Standard | undefined {
    return this.byId.get(id);
  }

  antiPattern(id: string): AntiPattern | undefined {
    return this.apById.get(id);
  }

  allStandards(): Standard[] {
    return [...this.byId.values()];
  }

  /** Extract a standard id (S{C}.{N}) at a position in a line, if any. */
  static standardAt(line: string, character: number): string | undefined {
    const re = /\bS\d+\.\d+\b/g;
    let m: RegExpExecArray | null;
    while ((m = re.exec(line)) !== null) {
      if (character >= m.index && character <= m.index + m[0].length) {
        return m[0];
      }
    }
    return undefined;
  }

  static looksLikeStandard(text: string): boolean {
    return STANDARD_RE.test(text);
  }

  private resolveIndexPath(): string | undefined {
    const configured = vscode.workspace
      .getConfiguration("governova")
      .get<string>("indexPath");
    if (configured && configured.trim()) {
      return path.isAbsolute(configured)
        ? configured
        : this.firstWorkspaceJoin(configured);
    }
    const candidates = [
      "compiled/constitution.json",
      ".ksdrill/compiled/constitution.json",
      "_governance/compiled/constitution.json",
    ];
    for (const folder of vscode.workspace.workspaceFolders ?? []) {
      for (const rel of candidates) {
        const full = path.join(folder.uri.fsPath, rel);
        if (fs.existsSync(full)) {
          return full;
        }
      }
    }
    return undefined;
  }

  private firstWorkspaceJoin(rel: string): string | undefined {
    const folder = vscode.workspace.workspaceFolders?.[0];
    return folder ? path.join(folder.uri.fsPath, rel) : undefined;
  }
}
