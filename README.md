bugzilla-ws
===========

A HTTP interface adapter for bugzilla xmlrpc

- Bugzilla::WebService::Bug
- Bugzilla::WebService::Bugzilla
- Bugzilla::WebService::Product
- Bugzilla::WebService::User
- Bugzilla::WebService::Util

GET /{namespace}/{function}?{params}

For example:

GET /bug/get?ids=1,2,3
 - will return the bugs with id 1,2,3 as JSON output.

Note:
 - If bugzilla server requires user login, please call /user/login?login=xxxx&password=xxx first to login.
 - Currently the cookie from bugzilla server is just maintained simply in a file, I don't have time to optimize it.
 - I appreciate any help.
