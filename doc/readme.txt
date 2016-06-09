--------------------------------------------------------------------------
Prerequisites
--------------------------------------------------------------------------
$ lsb_release -a
Description:	Ubuntu 14.04.1 LTS
$ python --version
Python 2.7.6

LDAP handling:

For Python2 --------
$ apt-get install python-ldap python-simplejson python-simplejson-doc

For Python3 ---------
$ apt-get install python3-ldap3 pythom3-simplejson

For Falcon based REST server:
$ apt-get install python-falcon uwsgi uwsgi-plugin-python

--------------------------------------------------------------------------
The Basic idea for usage of this utility
--------------------------------------------------------------------------

1) Check that the entry is not there - Student707

$> ./ldoper.py -m report -s sn=student707

Operation mode: report
LDAP search  using filter: sn=student707
[]

... no result was returned


2) Use Existing Student999 as a template to add new entry for Student708:

$> ./ldoper.py -m raw -s sn=student999 | sed -e 's/999/707/g' | ./ldoper.py -m add

Operation mode: add
Operation mode: report
LDAP search  using filter: sn=student999
Parse JSON text to Python data ------------
Try to add to LDAP:  {'mail': 'test.student707@students.example.com'}
   cn: test.student707
   userpassword: Notset2016
   user_type: student
   sn: Student707
   mail: test.student707@students.example.com
   givenname: Test
   description: xx
ATTRS:  {'description': 'xx', 'objectclass': ['top', 'person', 'inetorgperson'], 'userpassword': 'Notset2016', 'sn': 'Student707', 'mail': 'test.student707@students.example.com', 'givenname': 'Test', 'cn': 'test.student707'}
NEW  DN: cn=test.student707,ou=students,ou=users,dc=ad7,dc=local

... so the program was used to "report" data of an existing user (in JSON format), this data was slightly changed on the fly, and this modified data fed for the same program now in "add" mode


3) Check that Student707 is now there:

$> ./ldoper.py -m report -s sn=student707

Operation mode: report
LDAP search  using filter: sn=student707
[{"cn": ["test.student707"], "userpassword": ["Notset2016"], "user_type": ["student"], "sn": ["Student707"], "mail": ["test.student707@students.example.com"], "givenname": ["Test"], "description": ["xx"]}]

... now the new entry was found


--------------------------------------------------------------------------
REST server ----------------

$ apt-get intall python-falcon
$ apt-get intall python3-falcon

root@smxdc1:/media/sf_smxdc1/PycharmProjects/court7# python main.py 
Serving on 127.0.0.1:8000

---

Test:

root@smxdc1:# curl http://localhost:8000/things
[{"id": 1, "name": "Thingie"}, {"id": 2, "name": "Thinger"}]

----

gunicorn ldrest:app

  475  curl -i -X POST http://localhost:8000/ldoper -d '{"config": {"oper":"search"},"data":[{"id": 1,
"name": "Thingie"}, {"id": 2, "name": "Thinger"}]}'

-----------------------------------------
With python3, have to use the python3 gunicorn:
... http://docs.gunicorn.org/en/stable/install.html

$ apt-get install pip3
$ pip3 install gunicorn

Now  latest python3 aware gunicorn is in /usr/local/bin/gunicorn
... the apt-get gunicorn wants python2

-----------------------------------------
Start server (now Python 3):

root@smxdc1:~/PycharmProjects/court7# /usr/local/bin/gunicorn ldrest:app

[2016-05-25 15:05:57 +0700] [8607] [INFO] Starting gunicorn 19.6.0
[2016-05-25 15:05:57 +0700] [8607] [INFO] Listening at: http://127.0.0.1:8000 (8607)
[2016-05-25 15:05:57 +0700] [8607] [INFO] Using worker: sync
[2016-05-25 15:05:57 +0700] [8610] [INFO] Booting worker with pid: 8610
...

-----------------------------------------
Be client (do search, implicit mode is "raw", search filter set by "search"-paramter; data has now significance):

.../court7# curl -i -X POST http://localhost:8000/ldoper -d '{"config": {"search":"(cn=test.staff213)"},"data":[]}'

HTTP/1.1 200 OK
Server: gunicorn/19.6.0
Date: Wed, 25 May 2016 03:53:52 GMT
Connection: close
Access-Control-Allow-Origin: *
Content-Length: 323
Content-Type: application/json; charset=utf-8

"[{\"givenname\": [\"Test\"], \"user_type\": [\"staff\"], \"cn\": [\"test.staff213\"], \"displayname\": [\"Test Staff213\"], \"sn\": [\"Staff213\"], \"mail\": [\"test.staff213@hope.edu.kh\"], \"userpassword\": [\"Hope1234\"], \"__user_type\": [\"staff\"], \"description\": [\"HOPE circle\"], \"uid\": [\"test.staff213\"]}]"

---------------------
How to add a user via REST:
(... to test only (dry run), add parameter to config section:  "test": "1")

curl -i -X POST http://localhost:8000/ldoper -d \
''{"config": {"mode":"add"},"data":[{"displayname": ["Test Staff214"], "description": ["HOPE circle"], "sn": ["Staff214"], "user_type": ["staff"], "userpassword": ["Hope1234"], "mail": ["test.staff214@hope.edu.kh"], "cn": ["test.staff214"], "givenname": ["Test"], "uid": ["test.staff214"]}]}''

---------------------
Interactive HTML client with web browser:

file:///.../court7/html/ldoper.html

Contains the under the hood JSON / REST calls with a browser.
Two input / output sections ... one can be used to fetch the data, the other to add entries to AD/LDAP.


