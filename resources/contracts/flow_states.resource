*** Settings ***
Documentation    Canonical cross-layer flow-state values for onboarding and ETB automation.
...              Consumers compare and return these variables instead of duplicating string literals.
...              UI markers, environment names, and execution policies are intentionally out of scope.


*** Variables ***
${FLOW_STATE_NEXT}                               NEXT
${FLOW_STATE_NOT_OBSERVED}                       NOT_OBSERVED

${FLOW_STATE_AJI_001}                            AJI-001
${FLOW_STATE_GOD_005}                            GOD-005
${FLOW_STATE_GOD_013}                            GOD-013
${FLOW_STATE_RGI_104}                            RGI-104

${FLOW_STATE_PROFILE_LEFT_OR_NEXT}               PROFILE_LEFT_OR_NEXT_STATE_VISIBLE

${FLOW_STATE_PDPA_ACCEPT_NO_TRANSITION}          PDPA_ACCEPT_NO_TRANSITION
${FLOW_STATE_COMMON_ONBOARDING_COMPLETED}        COMMON_ONBOARDING_COMPLETED

${FLOW_STATE_SAVED}                              SAVED
${FLOW_STATE_ENVIRONMENT_BLOCKED}                ENVIRONMENT_BLOCKED
${FLOW_STATE_NEXT_SCREEN_UNKNOWN}                NEXT_SCREEN_UNKNOWN

${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}             CHECK_PDPA_CLAUSE_NO_6
${FLOW_STATE_INTRO_FACE_SCAN}                       INTRO_FACE_SCAN
${FLOW_STATE_CONFIRM_PIN}                        CONFIRM_PIN
${FLOW_STATE_PRODUCT_SELECTION}                  PRODUCT_SELECTION
${FLOW_STATE_COMPLETION_SUCCESS}                 COMPLETION_SUCCESS
${FLOW_STATE_EXACT_ERROR}                        EXACT_ERROR
${FLOW_STATE_LOADING_OR_INTERMEDIATE}            LOADING_OR_INTERMEDIATE
${FLOW_STATE_UNKNOWN}                            UNKNOWN
${FLOW_STATE_ENVIRONMENT_BACKEND_AJI_001}        ENVIRONMENT_BACKEND_AJI_001
${FLOW_STATE_REGISTRATION_SUCCESS}               REGISTRATION_SUCCESS
