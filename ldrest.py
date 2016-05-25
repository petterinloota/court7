import falcon
import json
from hopetools.hopeglob import Global
from ldmain import LdoperMain

class ThingsResource(object):

    """
    parser.add_argument("-m", "--mode", default="raw",  help="define the mode of operation: raw, report, add ( ... yet to come: modify)")
parser.add_argument("-s", "--search", default="objectclass=*",  help="define the search filter, default: objectclass=*")
parser.add_argument("-b", "--base", default=None,  help="define the LDAP search base DN")
parser.add_argument("-f", "--file", default=None, help="file to read the input data from; optionally stdin can be used")
parser.add_argument("-c", "--config", default='/etc/hope/ldap.conf', help="file to read the LDAP configuratin from")
parser.add_argument("-v", "--verbose", default=0, help="verbosity level - 0(default) or 1")
parser.add_argument("-T", "--test", default=0, help="Test only (default) or 1")
parser.add_argument("-o", "--options", default="", help="Options: [memberuid|posix_group]")

    """


    def analyze_input(self, raw_json):

        prm_map = {'mode': 'raw', 'search': '(cn=*)', 'base': None, 'config': '/etc/hope/ldap.conf', 'test': False, 'options': False}

        print(raw_json)

        config = raw_json['config']
        data = raw_json['data']

        print("DATA: ", data)
        print ("CONFIG: ", config)

        for prm in prm_map.keys():
            if prm in config:
                prm_map[prm] = config[prm]

        #for item in raw_json:
         #   print item
          #  print item['id']

        print ("MODE: ", prm_map['mode'])
        print ("SEARCH: ", prm_map['search'])

        ldoper = LdoperMain(mode=prm_map['mode'], search=prm_map['search'], config=prm_map['config'])
        ldoper.configObj.printOut()

        if prm_map.get('mode') == 'add':
            result = ldoper.addByList(data)
            print ("RESULT: ", result)
            return result

        formatObj = ldoper.fetch()
        print ("RESULT: ", formatObj.getJson(), "\n")

        return formatObj.getJson()

    def on_get(self, req, resp):
        """Handles GET requests"""
        print ("GET Query:", req.url)
        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = 'Hello world!'

    def on_post(self, req, resp):
        """Handles POST requests"""
        print ("POST Query:", req.url)
        # falcon.Request.url
        try:
            raw_json = req.stream.read()
            print ("POST RAW: ", raw_json)
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Error',
                ex.message)

        try:
            print('TYPE of data: ', type(raw_json))
            result_json = self.analyze_input(json.loads(raw_json.decode("utf-8"), encoding='utf-8'))
            # result_json = json.loads(raw_json, encoding='utf-8')

        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Malformed JSON',
                'Could not decode the request body. The '
                'JSON was incorrect.')



        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(result_json)
        # resp.body = json.dumps(result_json.encode('utf-8'), encoding='utf-8')

# falcon.API instances are callable WSGI apps
app = api = falcon.API()

# Resources are represented by long-lived class instances
things = ThingsResource()

# things will handle all requests to the '/things' URL path
api.add_route('/ldoper', things)
