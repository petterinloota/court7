--------------------------------------------------------------------------
Up to date version of this document
--------------------------------------------------------------------------

For a fresh version, see rather this: 
https://docs.google.com/document/d/1bouiOmFq3NQMgMdnEjLkaP6HC5BFjAAnA1XCuQamHXA

--------------------------------------------------------------------------
Prerequisites
--------------------------------------------------------------------------

Reference environment:
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

--------------------------------------------------------------------------
Configuration file
--------------------------------------------------------------------------

Example configuration --------------------

Here one example, more in the etc directory of the project.

{
"__start": "Not used, just start marker",
"host": "10.10.10.86",
"binddn": "CN=Administrator,CN=Users,DC=duckdc,DC=duck,DC=edu,DC=org",
"binddn_2": "Administrator@PPDC",
"basedn": "dc=duckdc,dc=duck,dc=edu,dc=org",
"searchbase": "ou=Duck,dc=duckdc,dc=duck,dc=edu,dc=org",
"rdnattr": "cn",
"transform_alias_attr": "samaccountname",
"override_rdn": "1",
"upn_domain": "duckdc.duck.org",
"bindpw": "XXX",
"maildomain": "duck.edu.org",
"maildomainmap": {"student": "students.duck.edu.org"},
"userou": "OU=Duck,dc=duckdc,dc=duck,dc=edu,dc=org",
"useroumap": {"staff": "ou=Staff,ou=Duck,dc=duckdc,dc=duck,dc=edu,dc=org", "student": "ou=Students,ou=Duck,dc=duckdc,dc=duck,dc=edu,dc=org"},
"user_objlist": ["top", "person", "organizationalperson", "user"],
"user_attrlist": ["uid", "uidnumber", "homedirectory", "useraccountcontrol", "unixhomedirectory", "loginshell", "gidnumber", "samaccountname", "msSFU30NisDomain", "mssfu30name" ],
"userattr_default_map": {"gidnumber": "1501", "loginshell": "/bin/bash", "msSFU30NisDomain": "duckdc", "useraccountcontrol": "66048"},
"groupattr_default_map": {"msSFU30NisDomain": "duckdc"},
"grouptype": "samba-ad",
"groupmemberattr": "member",
"groupou": "ou=groups,ou=duck,dc=duckdc,dc=duck,dc=edu,dc=org",
"__end": "Not used, just end marker"
}

Location (OU) for a new user Entry  -------------

The location of the new entry is defined by userou and useroumap parameters.
The userou defines the default location for new user entries.
With useroumap it is possible to define the location depending on the input data.

   "userou": "OU=Duck,dc=duckdc,dc=duck,dc=edu,dc=org",
   "useroumap": {"staff": "ou=Staff,ou=Duck,dc=duckdc,dc=duck,dc=edu,dc=org", "student": "ou=Students,ou=Duck,dc=duckdc,dc=duck,dc=edu,dc=org"},

If the input data contains attribute "user_type" (bigger priority) or "__user_type", the value of this parameter is the key by which the OU is defined based on the useroumap definition.

RDN of a new user entry -----------------

If user entry should be for instance "cn=john.smith,ou=staff,ou=default,DC=duckdc,DC=duck,DC=edu,DC=org", the RDN of the user entry DN is: cn=john.shmith and RDN attribute is "cn". Cn is perhaps the most common but for instance "uid" could be used as well.

   "rdnattr": "cn",

Next thing to be defined is how the value of this attribute is set. If the input data contains the value, then by default that is used.

If there is no cn parameter in the input data, cn is generated from "givenname" and  "sn" parameters and the result will be for example: donald.duck.

If there is a need to transform the entries so that earlier convention to have the natural name of a person as cn value (cn=Donald Duck) and start using perhaps more robust approach where cn is interpredted as username (cn=donald.duck), this can be accomplished with two new parameters:

   "override_rdn": "1",
   "transform_alias_attr": "samaccountname",

Now the RDN is overriden by a new value taken from "samaccountname" attribute and eventhough the input data would contain value for cn, that is overriden byt the value of the samaccountname parameter.

Managing groups - generating list of UIDs when searching a group -------------

Using following 

Creating a new group - where and how to store the memeber information ------------

The attribute and the contents of the attribute can be set with "grouptype" parameter and the attribute to store the members by "groupmemberattribute" parameter.
If the directory is of type AD, 

   "groupmemberattr": "member",
   "grouptype": "samba-ad",

Default for the value of the group member attribute is that the value is the username (uid) of the user. For example: memberuid: donald.duck, hewey.duck, ...
When the grouptype is "samba-ad", the value of the group member attribute will be the whole DN of the member entry, not just username. For example: member: cn=donald.duck,ou=Company,...

Moreover, to add AD group, cmd line option  "-o ad_group" have to be used.
For not-ad-group, the option is "-o group"

The members of the group have to be in the memberuid parameter of the input data.
To populate this parameter from data originally coming from this or some other AD, the cmd line option "-o memberuid_parse" can be used. This will populate the memberuid-parameter based on the member attribute values.




