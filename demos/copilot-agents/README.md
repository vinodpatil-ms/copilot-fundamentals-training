# Copilot Agents Demo

Use the following 3 files to setup your Copilot Agents demo. 
Paste the ISSUE.md file into a new issue in that repository. 

## What this demo shows
- Assign an issue to Copilot to start an agent task
- Monitor progress in AgentHQ
- Re-steer mid-session with a new requirement
- Review the resulting PR like a teammate’s work

## Demo files
- `ISSUE.md` contains the exact issue text to copy/paste into GitHub
- `STEER.md` contains the mid-session requirement change to paste while the agent is working

## Quick demo steps
1. Create a new GitHub Issue by copying the Title and Body from `ISSUE.md`
2. Assign the issue to Copilot to start the agent task
3. Open AgentHQ to monitor progress
4. Paste `STEER.md` into the agent session to re-steer the work
5. Review the PR diff for clarity, completeness, and constraints.
6. Verify the PR edited the README.md file by adding priority levels plus the steered examples. 

---

## Ticket Triage Policy

### Severity levels
| Severity | Definition |
|----------|-----------|
| High | Blocks key workflows or causes data loss |
| Medium | Meaningful user impact; workarounds exist |
| Low | Minor annoyance with an easy workaround |

### Priority levels
| Priority | Definition |
|----------|-----------|
| P0 | Critical — service down or data loss; page on-call immediately |
| P1 | High — major feature broken, no workaround; fix within 24 hours |
| P2 | Medium — impaired functionality, workaround available; fix within the sprint |
| P3 | Low — cosmetic or minor inconvenience; schedule as capacity allows |

### Severity → Priority mapping
| Severity | Default Priority |
|----------|----------------|
| High | P0 or P1 |
| Medium | P2 |
| Low | P3 |

### How to triage in 60 seconds
1. Read the title and description
2. Assign a Severity (High / Medium / Low)
3. Use the mapping above to set the default Priority
4. Escalate to P0 if users are blocked in production right now
5. Label the ticket and assign an owner
