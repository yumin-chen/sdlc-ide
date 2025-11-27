package template.authz

import future.keywords.every

# By default, deny the request
default allow = false

# Allow is true if all the policy rules are met
allow {
    # 1. Actor must have the required role for the action
    actor_has_required_role

    # 2. Template must not contain executable code
    not contains_forbidden_fields

    # 3. LLM-authored templates must not define permissions or lifecycles
    not llm_violates_policy

    # 4. Lifecycle transitions must be permitted by the Core DAG
    lifecycle_is_valid
}

# Define the required role for each action
required_role_for_action := {
    "register_template": "template_author"
}

# 1) Actor must be bound to a role allowed to perform action.
actor_has_required_role {
  required := required_role_for_action[input.action]
  required != ""
  # Check 1: Role directly assigned to the actor
  required_in_actor_roles(required)
} else {
  required := required_role_for_action[input.action]
  required != ""
  # Check 2: Principal is bound to the role in the template, either directly or via group membership
  required_in_template_bindings(required)
}

# Check if the actor's principal ID is a member of the required group/principal
principal_is_member_of(principal_id, required_principal) {
    principal_id == required_principal
}
principal_is_member_of(principal_id, required_principal) {
    # Check if required_principal is a group (e.g., 'team:...') and the actor is a member
    data.identity.groups[required_principal][_] == principal_id
}

# The actor must have the required role directly in their claims
required_in_actor_roles(required) {
  some i
  input.actor.roles[i] == required
}

# The required role must be assigned to the actor (or their team) in the template's bindings
required_in_template_bindings(required) {
  some j
  binding := input.template.bindings[j]
  binding.role == required
  principal_is_member_of(input.actor.principal_id, binding.principal)
}

# 2) Template must not contain executable code
contains_forbidden_fields {
    input.template.spec.exec
}

# 3) LLM-authored templates must not define permissions or lifecycles
llm_violates_policy {
    input.template.provenance.created_by == "llm"
    count(input.template.bindings) > 0
}
llm_violates_policy {
    input.template.provenance.created_by == "llm"
    count(input.template.lifecycle.transitions) > 0
}

# 4) Lifecycle transitions must be permitted by the Core DAG
lifecycle_is_valid {
    # Check if all transitions in the template are present in the core_dag
    every transition in input.template.lifecycle.transitions {
        some i
        data.core_dag.transitions[i] == transition
    }
}

# Provide reasons for denial
reasons[msg] {
    not actor_has_required_role
    msg := "actor not bound to required role"
}
reasons[msg] {
    contains_forbidden_fields
    msg := "template contains forbidden executable fields"
}
reasons[msg] {
    llm_violates_policy
    msg := "LLM authored permission/lifecycle definitions are forbidden"
}
reasons[msg] {
    not lifecycle_is_valid
    msg := "lifecycle transitions not permitted by Core DAG"
}
