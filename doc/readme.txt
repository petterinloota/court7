--------------------------------------------------------------------------
Prerequisites
--------------------------------------------------------------------------
$ lsb_release -a
Description:	Ubuntu 14.04.1 LTS
$ python --version
Python 2.7.6

$ apt-get install python-ldap python-simplejson python-simplejson-doc

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

