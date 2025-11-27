package sdlc.governance

default allow = false

# helper: is path ADR?
is_adr_path(path) {
  startswith(path, "docs/adr/")
}

# helper: determine if event is PR merge
is_pr_merge(input) {
  input.event_type == "pull_request"
  input.action == "closed"
  input.pull_request.merged == true
}

# helper: determine if push was a merge commit tied to PR (depends on git metadata available)
is_merge_commit_with_pr(input) {
  # best-effort: check if push payload contains "merged_by_pr": true or commit message contains "Merge pull request"
  input.event_type == "push"
  some i
  input.commits[i].message
  contains(input.commits[i].message, "Merge pull request")
}

# helper: check if any changed file matches ADR path
any_adr_changed {
  some i
  input.changed_files[i]
  is_adr_path(input.changed_files[i])
}

# main allow rule
allow {
  # no ADR files changed -> ok
  not any_adr_changed
}

allow {
  # ADR files changed and event is a PR merge
  any_adr_changed
  is_pr_merge(input)
}

allow {
  # ADR files changed and push is merge commit with PR tag (best-effort)
  any_adr_changed
  is_merge_commit_with_pr(input)
}
