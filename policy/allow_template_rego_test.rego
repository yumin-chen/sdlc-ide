package template.authz

test_allow_valid_registration {
    allow with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:alice", "roles": ["template_author"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "github:alice"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["draft", "review"]] },
            "spec": {"kind": "K8sDeployment"}
        }
    } with data.core_dag as {
        "transitions": [ ["draft","review"], ["review","approved"] ]
    }
}

test_deny_unbound_actor {
    not allow with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:bob", "roles": ["runtime_operator"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "github:alice"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["draft", "review"]] },
            "spec": {"kind": "K8sDeployment"}
        }
    } with data.core_dag as { "transitions": [["draft","review"]] } with data.identity as {
        "groups": { "team:platform": ["github:alice"] }
    }
    reasons[_] == "actor not bound to required role" with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:bob", "roles": ["runtime_operator"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "github:alice"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["draft", "review"]] },
            "spec": {"kind": "K8sDeployment"}
        }
    } with data.core_dag as { "transitions": [["draft","review"]] } with data.identity as {
        "groups": { "team:platform": ["github:alice"] }
    }
}

test_deny_exec_code {
    not allow with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:alice", "roles": ["template_author"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "github:alice"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["draft", "review"]] },
            "spec": {"kind": "K8sDeployment", "exec": "rm -rf /"}
        }
    } with data.core_dag as { "transitions": [["draft","review"]] }
    reasons[_] == "template contains forbidden executable fields" with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:alice", "roles": ["template_author"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "github:alice"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["draft", "review"]] },
            "spec": {"kind": "K8sDeployment", "exec": "rm -rf /"}
        }
    } with data.core_dag as { "transitions": [["draft","review"]] }
}

test_deny_llm_violates_policy {
    not allow with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:alice", "roles": ["template_author"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "llm"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["draft", "review"]] },
            "spec": {"kind": "K8sDeployment"}
        }
    } with data.core_dag as { "transitions": [["draft","review"]] }
    reasons[_] == "LLM authored permission/lifecycle definitions are forbidden" with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:alice", "roles": ["template_author"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "llm"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["draft", "review"]] },
            "spec": {"kind": "K8sDeployment"}
        }
    } with data.core_dag as { "transitions": [["draft","review"]] }
}

test_deny_invalid_lifecycle {
    not allow with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:alice", "roles": ["template_author"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "github:alice"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["approved", "draft"]] },
            "spec": {"kind": "K8sDeployment"}
        }
    } with data.core_dag as {
        "transitions": [ ["draft","review"], ["review","approved"] ]
    }
    reasons[_] == "lifecycle transitions not permitted by Core DAG" with input as {
        "action": "register_template",
        "actor": {"principal_id": "github:alice", "roles": ["template_author"]},
        "template": {
            "id": "test/valid:v1",
            "provenance": {"created_by": "github:alice"},
            "bindings": [{"role": "template_author", "principal": "github:alice"}],
            "lifecycle": { "transitions": [["approved", "draft"]] },
            "spec": {"kind": "K8sDeployment"}
        }
    } with data.core_dag as {
        "transitions": [ ["draft","review"], ["review","approved"] ]
    }
}
