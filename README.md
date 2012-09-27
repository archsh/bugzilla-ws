bugzilla-ws
===========

A HTTP interface adapter for bugzilla xmlrpc

Bugzilla::WebService::Bug
Bugzilla::WebService::Bugzilla
Bugzilla::WebService::Product
Bugzilla::WebService::User
Bugzilla::WebService::Util

GET /{namespace}/{function}?{params}

For example:

GET /bug/get?ids=1,2,3
 - will return the bugs with id 1,2,3 as JSON output.
