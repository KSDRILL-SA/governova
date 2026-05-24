/**
 * Governova — compiled constitutional index types.
 *
 * DO NOT EDIT. Generated from compiled/constitution.schema.json by
 * `governova-codegen`. The source of truth is
 * scripts/governova_compile/schema.py.
 */

/**
 * Semantic version of the schema.
 */
export type SchemaVersion = string;
export type CompiledAt = string;
/**
 * Git SHA of the source tree.
 */
export type SourceCommitSha = string | null;
/**
 * SHA-256 of the index body (everything except this field).
 */
export type Checksum = string;
/**
 * Slug, e.g. 'format-specification'.
 */
export type Id = string;
export type Title = string;
export type Path = string;
/**
 * One-line description.
 */
export type Summary = string;
export type Framework = FrameworkPrimitive[];
export type Id1 = string;
/**
 * Numeric constitution number (0–99).
 */
export type Number = number;
export type Name = string;
/**
 * The four phases per C0 §6.
 */
export type Phase = "0" | "1" | "2" | "3";
/**
 * Full document title, e.g. 'C1 — Engineering Standards'.
 */
export type Document = string;
export type Organisation = string;
export type Version = string;
/**
 * Lifecycle status of a constitutional document.
 */
export type DocumentStatus = "DRAFT" | "LOCKED" | "DEPRECATED";
export type LockedDate = string | null;
export type NextReview = string | null;
export type AppliesTo = string | null;
export type PairedWith = string | null;
/**
 * Repo-relative path to the source markdown file.
 */
export type Path1 = string;
/**
 * Position in C0 §7.1 conflict-resolution hierarchy. 1 = highest authority.
 */
export type HierarchyRank = number | null;
/**
 * True if this constitution has paired stack bindings.
 */
export type BindsImplementation = boolean;
export type Id2 = string;
export type Title1 = string;
/**
 * The owning constitution, e.g. 'C01'.
 */
export type ConstitutionId = string;
/**
 * Standard priority — how important is the standard itself.
 *
 * Mirrors C0 §2.3. Distinct from Severity (which classifies incidents).
 */
export type Priority = "Critical" | "High" | "Standard" | "Guidance";
/**
 * Scope — free-form, e.g. 'Both Stacks', 'Next.js Only', 'All Systems'.
 */
export type AppliesTo1 = string;
/**
 * Original phase string from source, e.g. 'Phase 0 — Foundation'.
 */
export type PhaseLabel = string | null;
export type StandardId = string;
/**
 * Optional inline description, e.g. the parenthetical in source markdown.
 */
export type Description = string | null;
/**
 * Standards this one cannot function without.
 */
export type DependsOn = Reference[];
/**
 * Enforcement mechanisms, e.g. ['CI', 'ESLint', 'Code Review'].
 */
export type EnforcedBy = string[];
/**
 * The standard text — what must be true.
 */
export type Statement = string;
/**
 * Why this standard exists — production consequence.
 */
export type Rationale = string;
export type Id3 = string;
/**
 * What the failure looks like in practice.
 */
export type Description1 = string;
/**
 * The standard this anti-pattern violates.
 */
export type ParentStandardId = string;
export type AntiPatterns = AntiPattern[];
export type CrossReferences = Reference[];
/**
 * True if the standard was authored in blockquote shorthand (`> **S{C}.{N}** — ...`) and therefore lacks a full attribute table, rationale, and dedicated anti-pattern block.
 */
export type Abbreviated = boolean;
/**
 * Repo-relative path to the source markdown file.
 */
export type SourcePath = string;
/**
 * 1-indexed line number where the standard heading begins.
 */
export type SourceLine = number;
export type Standards = Standard[];
export type Constitutions = Constitution[];
export type Stack = string;
export type BindsConstitution = string;
export type Name1 = string;
export type Path2 = string;
export type Id4 = string;
export type Title2 = string;
/**
 * Standards this practice operationalises.
 */
export type SatisfiesStandards = string[];
export type SourcePath1 = string;
export type SourceLine1 = number;
export type Practices = Practice[];
/**
 * e.g. 'S2.7/fastapi'.
 */
export type Id5 = string;
export type BindsStandard = string;
/**
 * Stack identifier, e.g. 'fastapi', 'nextjs'.
 */
export type Stack1 = string;
/**
 * How the standard is met in this stack.
 */
export type SatisfiesBy = string;
export type AntiPattern1 = string | null;
export type Bindings = ImplementationBinding[];
export type Implementations = Implementation[];
export type Domains = Constitution[];
export type Id6 = string;
export type Name2 = string;
/**
 * When this runbook is activated.
 */
export type Trigger = string;
export type Path3 = string;
export type Runbooks = Runbook[];
export type Id7 = string;
export type Name3 = string;
/**
 * e.g. 'ACCEPTED', 'PROPOSED'.
 */
export type Status = string | null;
export type Path4 = string;
export type Adrs = ADR[];
/**
 * Conflict-resolution order from C0 §7.1 (highest authority first).
 */
export type Hierarchy = string[];
export type StandardsExtracted = number;
export type AntiPatternsExtracted = number;
export type BindingsExtracted = number;
export type ReferencesResolved = number;
export type ReferencesUnresolved = number;
export type LinksChecked = number;
export type LinksBroken = number;
/**
 * Incident / violation severity — how severe is the failure.
 *
 * Mirrors `framework/severity-model.md`. Distinct from Priority.
 */
export type Severity = "SEV0" | "SEV1" | "SEV2" | "SEV3";
/**
 * Short machine-readable code, e.g. 'orphan-reference'.
 */
export type Code = string;
export type Message = string;
export type SourcePath2 = string | null;
export type SourceLine2 = number | null;
export type Errors = IntegrityIssue[];
export type Warnings = IntegrityIssue[];

/**
 * Machine-readable form of the Governova constitutional database, schema version 1.0.0. See https://governova.dev/docs/schema.
 */
export interface GovernovaCompiledConstitutionalIndex {
  schema_version?: SchemaVersion;
  compiled_at: CompiledAt;
  source_commit_sha?: SourceCommitSha;
  checksum: Checksum;
  framework?: Framework;
  constitutions?: Constitutions;
  implementations?: Implementations;
  domains?: Domains;
  runbooks?: Runbooks;
  adrs?: Adrs;
  hierarchy?: Hierarchy;
  phases?: Phases;
  integrity?: IntegrityReport;
}
/**
 * A Layer 1 framework primitive — universal, stack-agnostic.
 */
export interface FrameworkPrimitive {
  id: Id;
  title: Title;
  path: Path;
  summary: Summary;
}
/**
 * A core constitution document (C00–C10) or a domain extension.
 */
export interface Constitution {
  id: Id1;
  number: Number;
  name: Name;
  /**
   * None for C0; otherwise 0–3.
   */
  phase?: Phase | null;
  header: DocumentHeader;
  path: Path1;
  hierarchy_rank?: HierarchyRank;
  binds_implementation?: BindsImplementation;
  standards?: Standards;
}
/**
 * The identity block at the top of every constitution / implementation guide.
 */
export interface DocumentHeader {
  document: Document;
  organisation?: Organisation;
  version?: Version;
  status?: DocumentStatus;
  locked_date?: LockedDate;
  next_review?: NextReview;
  applies_to?: AppliesTo;
  paired_with?: PairedWith;
}
/**
 * A governing statement in a constitution.
 *
 * Mirrors the canonical block defined in C0 §3.1.
 */
export interface Standard {
  id: Id2;
  title: Title1;
  constitution_id: ConstitutionId;
  priority: Priority;
  applies_to: AppliesTo1;
  /**
   * The phase the owning constitution belongs to. None for C0.
   */
  phase?: Phase | null;
  phase_label?: PhaseLabel;
  depends_on?: DependsOn;
  enforced_by?: EnforcedBy;
  statement: Statement;
  rationale?: Rationale;
  anti_patterns?: AntiPatterns;
  cross_references?: CrossReferences;
  abbreviated?: Abbreviated;
  source_path: SourcePath;
  source_line: SourceLine;
}
/**
 * A reference to another standard, with optional inline description.
 *
 * Used in `depends_on` and `cross_references` fields. The description is
 * typically the parenthetical hint shown in the source markdown.
 */
export interface Reference {
  standard_id: StandardId;
  description?: Description;
}
/**
 * A documented failure mode of a standard.
 */
export interface AntiPattern {
  id: Id3;
  description: Description1;
  parent_standard_id: ParentStandardId;
}
/**
 * A stack-specific implementation guide for one core constitution.
 *
 * Current guides express the implementation layer as Practices (`P{C}.{N}`).
 * The `bindings` field supports the `S{C}.{N}/{stack}` format from
 * `framework/format-specification.md` for future spec-compliant guides.
 */
export interface Implementation {
  stack: Stack;
  binds_constitution: BindsConstitution;
  name: Name1;
  header: DocumentHeader;
  path: Path2;
  practices?: Practices;
  bindings?: Bindings;
}
/**
 * An operational how-to in an implementation guide. C0 §2.1.
 *
 * A practice references the standard(s) it satisfies via inline `S{C}.{N}`
 * citations in its section.
 */
export interface Practice {
  id: Id4;
  title: Title2;
  satisfies_standards?: SatisfiesStandards;
  source_path: SourcePath1;
  source_line: SourceLine1;
}
/**
 * How a universal standard is satisfied in a specific stack.
 */
export interface ImplementationBinding {
  id: Id5;
  binds_standard: BindsStandard;
  stack: Stack1;
  satisfies_by: SatisfiesBy;
  anti_pattern?: AntiPattern1;
}
/**
 * An operational response procedure.
 */
export interface Runbook {
  id: Id6;
  name: Name2;
  trigger: Trigger;
  path: Path3;
}
/**
 * An Architecture Decision Record.
 */
export interface ADR {
  id: Id7;
  name: Name3;
  status?: Status;
  path: Path4;
}
/**
 * Mapping of phase → constitutions in that phase.
 */
export interface Phases {
  [k: string]: string[];
}
/**
 * Aggregate integrity status for one compile run.
 */
export interface IntegrityReport {
  standards_extracted?: StandardsExtracted;
  anti_patterns_extracted?: AntiPatternsExtracted;
  bindings_extracted?: BindingsExtracted;
  references_resolved?: ReferencesResolved;
  references_unresolved?: ReferencesUnresolved;
  links_checked?: LinksChecked;
  links_broken?: LinksBroken;
  errors?: Errors;
  warnings?: Warnings;
}
/**
 * A single integrity finding from the compile / validate pipeline.
 */
export interface IntegrityIssue {
  severity: Severity;
  code: Code;
  message: Message;
  source_path?: SourcePath2;
  source_line?: SourceLine2;
}
