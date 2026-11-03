# Daily use

## A normal day

1. Look at Today — on the dashboard page, in `TODAY.md`, or in Obsidian. Do the Focus tasks first.
2. Open the project's own Claude session (or a new one in its folder) and work.
3. At the end, Claude updates `LOG.md`, `STATUS.md` and, if something durable came up, `MEMORY.md`. If it forgets,
   say **"update status"**.
4. Refresh: **"run the daily brief"**, or let the scheduled run do it (see [scheduling.md](scheduling.md)).

## Weekly (Friday)

Read the scorecard. Did the Focus metric move? Is the Test on track for its pass rule? Is any Obligation deadline
close? Change one thing for next week. Update `current:` for the Focus and the Test if a session has not.

## Things you will say to Claude

| You say | What happens |
|---|---|
| "set up this project" (in a new `NNN Name` folder) | the four files are created and filled from the folder's documents; lane defaults to Parked |
| "update status" | the end-of-session procedure runs |
| "remember this" | the fact goes into `MEMORY.md` (or an entity note if it is shared) |
| "add that to the playbook" | a `## Promote` line is written; the next build files it |
| "run the daily brief" | the build runs, Today and the scorecard are shown, the page is refreshed |
| "make 004 the Focus" / "park 006 until March" | the lane changes, because you asked |
| "close 007" | `status: done`; what remains is recorded in its Notes |

## Changing the Focus

Only one project can be the Focus. To switch, decide what happens to the current one (Parked with a review date, or
Test, or done) and say so. The build flags two Focus projects until you choose.

## A new idea

Create the next numbered folder and say "set up this project". It starts **Parked** with a review date. That is the
point: new ideas are recorded, not started.
