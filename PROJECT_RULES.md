# Mandatory Project Save, Checkpoint, and Recovery Rules

**Project Name**: Delhi-NCR Air Quality Analysis  
**Project Root**: `D:\delhi-ncr-aqi-analysis`  
**Backup Root**: `D:\delhi-ncr-aqi-analysis-backups`  
**Applicability**: Permanent rules governing all current and future development stages.

---

## 1. Session Initialization and File Integrity
- At the start of **every new session or resumption**, the agent must read:
  1. `PROJECT_RULES.md`
  2. `PROJECT_STATUS.md`
  3. `HANDOFF.md`
- Inspect actual project files on disk and check `git status` / `git log` before writing any new code or making changes.
- Never rely on conversation context history as the sole source of project state.
- Never delete, overwrite, or restart completed work from scratch merely because a session restarted.

---

## 2. Continuous Saving Principle
- Save code, scripts, configs, reports, and documentation directly to disk as meaningful chunks are completed.
- Do not leave important logic in chat buffers, temporary directories, or unsaved memory.
- Save progress before starting long-running or multi-file operations.
- When fixing a bug, immediately save the fix and re-execute the affected tests.
- Raw datasets (`data/raw/`) and verified deliverables must never be overwritten or deleted.
- Verify that created files physically exist on disk before claiming an operation succeeded.

---

## 3. Maintaining `PROJECT_STATUS.md`
After every meaningful milestone or stage, update `PROJECT_STATUS.md` with:
- Overall project completion progress.
- Current stage name and status: `Not Started`, `In Progress`, `Blocked`, or `Verified Complete`.
- Completed vs. remaining tasks.
- Manifest of files created, modified, or removed.
- Exact commands executed and their output summaries.
- Test outcomes (passing counts and any failures).
- Blockers, data constraints, and limitations.
- Exact prioritized next actions.
- Clearly distinguish completed tasks from planned tasks.

---

## 4. Maintaining `HANDOFF.md`
After every meaningful milestone, update `HANDOFF.md` so any new agent session can immediately resume work:
- Project objective, technology stack, and root directory.
- Current stage and exact stopping point.
- Architectural and analytical decisions taken.
- Dataset sources, licensing terms, and cleaning rules.
- Key file paths and execution commands.
- Test suite outcomes.
- Blockers or unfinished components.
- The single, concrete, prioritized task the next session must execute first.

---

## 5. Local Git Checkpoints
At the end of every completed stage:
1. Run `git status` and inspect modified files.
2. Ensure `.gitignore` excludes secrets, virtual environments, caches (`__pycache__`), raw datasets, and temporary files.
3. Review changes and run the full test suite.
4. Stage only appropriate files.
5. Create a descriptive local commit message (e.g., `feat(stage-X): ...`).
6. Record the commit hash in `PROJECT_STATUS.md` and `HANDOFF.md`.
7. **Never push to GitHub without explicit user authorization.**

---

## 6. Stage Backup Archives
At the end of every completed stage:
- Create a timestamped ZIP archive in `D:\delhi-ncr-aqi-analysis-backups\`.
- Use naming format: `<stage-id>-<YYYY-MM-DD>.zip` (e.g., `stage-2a-2026-10-22.zip`).
- **Include**: source code, SQL scripts, tests, documentation, configuration, sample data, and lightweight processed dimensions/metrics.
- **Exclude**: `.git/`, `data/raw/*`, virtual environments, caches, `.env` files, and multi-megabyte raw binaries reconstructible via ingestion scripts.
- **Verify**: Confirm the ZIP archive exists, has non-zero size, and can be read.
- Never overwrite an existing backup archive.

---

## 7. Mandatory End-of-Stage Sequence
Before marking ANY stage complete:
1. Save all modified files to disk.
2. Run all feasible automated tests and validation checks.
3. Record actual command outputs and test results.
4. Update `PROJECT_STATUS.md`.
5. Update `HANDOFF.md`.
6. Review Git status and create a local checkpoint commit.
7. Create and verify the stage ZIP backup in `D:\delhi-ncr-aqi-analysis-backups\`.
8. Confirm that all documentation, code, and backup files physically exist.
9. Deliver a handover summary containing: stage status, saved files, commit hash, backup path, test results, and next step.

---

## 8. Handling "SAVE CHECKPOINT" / Early Interruption
If the user sends `"SAVE CHECKPOINT"`:
- Stop beginning new tasks immediately.
- Save current working files to disk.
- Update `PROJECT_STATUS.md` and `HANDOFF.md` recording partial progress, interrupted commands, and exact state.
- Create a partial Git commit and backup archive if safe.
- Report what was saved, what remains unfinished, and how to resume.
- Never claim that partially completed work is finished.

---

## 9. Session Recovery Procedure
When opening or resuming the project:
1. Read `PROJECT_RULES.md`, `PROJECT_STATUS.md`, and `HANDOFF.md`.
2. Run `git status` and `git log` to inspect local repository state.
3. Verify that the files reported in the last checkpoint match the disk.
4. Pick up the first unfinished task from `HANDOFF.md`.
5. Preserve all existing architecture and decisions unless a documented issue mandates revision.
