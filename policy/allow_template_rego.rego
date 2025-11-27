package template.authz

import data.core_dag

default allow = false

#
# Main Entrypoint: Allow is true if there are no reasons to deny.
#
allow {
    count(reasons) == 0
}

#
# Reason Generation: Each rule adds a reason for denial if a constraint is violated.
#
reasons contains msg {
    not actor_has_required_role
    msg := "actor not bound to required role"
}

reasons contains msg {
    template_contains_forbidden_fields
    msg := "template contains forbidden executable fields"
}

reasons contains msg {
    llm_authored_privileged_fields
    msg := "LLM authored permission/lifecycle definitions are forbidden"
}

reasons contains msg {
    not lifecycle_is_valid
    msg := "lifecycle transitions not permitted by Core DAG"
}

#
# Constraint 1: Actor Role Verification
#
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

# Helper: Map actions to required roles.
required_role_for_action := {
    "register_template": "template_author"
}

# Helper: Check if the actor's principal ID is a member of the required group/principal
principal_is_member_of(principal_id, required_principal) {
    principal_id == required_principal
}
principal_is_member_of(principal_id, required_principal) {
    # Check if required_principal is a group (e.g., 'team:...') and the actor is a member
    data.identity.groups[required_principal][_] == principal_id
}

# Helper: The actor must have the required role directly in their claims
required_in_actor_roles(required) {
  some i
  input.actor.roles[i] == required
}

# Helper: The required role must be assigned to the actor (or their team) in the template's bindings
required_in_template_bindings(required) {
  some j
  binding := input.template.bindings[j]
  binding.role == required
  principal_is_member_of(input.actor.principal_id, binding.principal)
}

#
# Constraint 2: Forbidden Fields
#
template_contains_forbidden_fields {
    _ = input.template.spec.exec
}

#
# Constraint 3: LLM Authorship Restrictions
#
llm_authored_privileged_fields {
    input.template.provenance.created_by == "llm"
    # LLMs cannot define bindings or lifecycle transitions
    (count(input.template.bindings) > 0; count(input.template.lifecycle.transitions) > 0)
}

#
# Constraint 4: Core DAG Lifecycle Validation
#
lifecycle_is_valid {
    # If no transitions are defined, it's valid by default.
    count(input.template.lifecycle.transitions) == 0
} else {
    # Every defined transition must exist in the core_dag
    every transition in input.template.lifecycle.transitions {
        some i
        core_dag.transitions[i] == transition
    }
}
