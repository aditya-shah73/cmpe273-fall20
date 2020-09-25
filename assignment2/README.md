# Assignment 2

## Requirements

This is a low-code/no-code HTTP client application that supports these features:

* Outbound HTTP GET calls
* Handle logic based on the response as INPUT.
* Trigger OUTPUT event based on the logic.
* Scheduler to execute the steps.

_Flow Syntax_

```yaml
Step:
 id: 1
 type: HTTP_CLIENT
 method: GET
 outbound_url: http://requestbin.com/
 condition:
  if:
    equal:
      left: http.response.code
      right: 200
  then:
    action: print
    data: http.response.body
  else:
    action: print
    data: "Error"

Scheduler:
  when: "5 * * * *"
  step_id_to_execute: [ 1 ]
```

## How to execute Flow HTTP Client

```
pipenv shell
pipenv install
python httpflow.py input.yaml
```

### Expected Output

Print the output in every five minutes.

```
Response body

OR

Error
```
