package main

default allow = false

allow if {
    input.USER.USER_ROLE == "USER_ROLE_MANAGER"
    input.ACTION == "ACTION_EDIT"
}
