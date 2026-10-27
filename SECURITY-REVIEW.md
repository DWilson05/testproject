# Security Review

## Scope

Focused review of `function_app.py` and the selected response branch:
`return make_response(existing, 200)`.

## Findings

### HIGH — API authentication can be bypassed when `API_KEY` is unset

- **Location:** `function_app.py`, lines 49–51
- **Confidence:** 9/10
- **Issue:** The authorization check compares the incoming `x-api-key` header
  directly with `os.environ.get("API_KEY")`. If `API_KEY` is not configured
  and the caller omits the header, both values are `None`, so the comparison
  succeeds. This would expose the burger CRUD endpoints to unauthenticated
  callers.
- **Recommendation:** Fail closed when `API_KEY` or the request header is
  missing. Configure the key through deployment secret settings or a Key Vault
  reference; do not rely on a local settings file.

## Selected line

`return make_response(existing, 200)` is not independently problematic based
on the reviewed context. Its security depends on the surrounding authorization
and data-access logic; the reported issue is the authorization check above it.

## Credential check

No credential values were found in the tracked files during this focused
review. The local settings file contains a local `API_KEY` configuration but
is ignored and does not establish that the deployed application has the
setting.
