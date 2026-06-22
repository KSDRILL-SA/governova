/** Tree data provider for the Governova "Standards" sidebar: Constitution → Standard. */
import * as vscode from "vscode";
import { Constitutions, Standard } from "./constitution";

type Node = ConstitutionNode | StandardNode;

class ConstitutionNode {
  readonly kind = "constitution";
  constructor(public readonly id: string, public readonly label: string, public readonly count: number) {}
}

class StandardNode {
  readonly kind = "standard";
  constructor(public readonly standard: Standard) {}
}

export class StandardsTreeProvider implements vscode.TreeDataProvider<Node> {
  private _onDidChange = new vscode.EventEmitter<Node | undefined | void>();
  readonly onDidChangeTreeData = this._onDidChange.event;

  constructor(private readonly cons: Constitutions) {}

  refresh(): void {
    this._onDidChange.fire();
  }

  getTreeItem(node: Node): vscode.TreeItem {
    if (node.kind === "constitution") {
      const item = new vscode.TreeItem(
        `${node.id} — ${node.label}`,
        vscode.TreeItemCollapsibleState.Collapsed
      );
      item.description = `${node.count}`;
      item.iconPath = new vscode.ThemeIcon("law");
      item.contextValue = "constitution";
      return item;
    }
    const s = node.standard;
    const item = new vscode.TreeItem(`${s.id} — ${s.title}`, vscode.TreeItemCollapsibleState.None);
    item.tooltip = new vscode.MarkdownString(`**${s.id} — ${s.title}**\n\n${s.statement}`);
    item.iconPath = new vscode.ThemeIcon("symbol-constant");
    item.command = {
      command: "governova.openStandard",
      title: "Open Standard",
      arguments: [s.id],
    };
    return item;
  }

  getChildren(node?: Node): Node[] {
    if (!this.cons.loaded) {
      return [];
    }
    if (!node) {
      return this.cons.constitutions
        .filter((c) => c.standards.length > 0)
        .map((c) => new ConstitutionNode(c.id, c.name, c.standards.length));
    }
    if (node.kind === "constitution") {
      const c = this.cons.constitutions.find((x) => x.id === node.id);
      return (c?.standards ?? []).map((s) => new StandardNode(s));
    }
    return [];
  }
}
