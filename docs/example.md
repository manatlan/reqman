# A classic example

Here is a classic config, with oauth2 flow authentification, and two mode switches.

When reqman is executed without switches (`reqman test.yml`):

  * It will target the server on localhost.
  * It will use a default access_token, for development


When reqman is executed with a switch 'prod' (`reqman test.yml -prod`):

  * It will target the server on example.com (root overriden)
  * It will try to obtain a access_token on authorization server (via BEGIN procedure)


## A reqman.conf
```yaml
root:                 http://localhost:8080

token:                # jwt token for local dev
  token_type:         Bearer
  access_token:       eyJhbGciOiJIUzI1NiIsInR6cCI6IkpXVCJ9.eyJzdWIiOiIxMzUwNjg4MjciLCJjZGV0YWIiOiIxNjI3NSIsImFwcGlkIjoicG9zdGVfbG9jYWwifQ.XMPNGpB5TUbmm08h2s79KYol32MQaRT_CvhAoTBBBnI

headers:
  Content-Type:       application/json; charset=utf-8
  x-hello:            it's me
  Authorization:      <<token.token_type>> <<token.access_token>>

switches:
  prod:
    doc:                Test in production
    root:               https://example.com

    BEGIN:
      POST:             https://authorization.server.example.com/oauth/token
      headers:
        Content-Type:   application/x-www-form-urlencoded
      body:             grant_type=client_credentials&client_id=dbfa1d28-c815-4b61-a435-0b2b761d30ab&client_secret=cbe46cde-affb-4324-8f26-f69ace80f1ce
      tests:
        - status:       200
      save:             token
```

## And a yml test file
```yaml
- GET: /api/pets/v1/list
  tests:
    - status: 200
  save:
    pets: <<json.items>>

- GET: /api/pets/v1/info/<<id>>
  params:
    id: <<json.items.0.id>>
 
```
