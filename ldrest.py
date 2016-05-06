import falcon
import json

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

        valid_config_prm_list = ['mode', 'search', 'base', 'file', 'config', 'verbose', 'test', 'options']

        print raw_json

        config = raw_json['config']
        data = raw_json['data']

        print "DATA: ", data
        print "CONFIG: ", config

        #for item in raw_json:
         #   print item
          #  print item['id']


    def on_get(self, req, resp):
        """Handles GET requests"""
        print "GET Query:", req.url
        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = 'Hello world!'

    def on_post(self, req, resp):
        """Handles POST requests"""
        print "POST Query:", req.url
        # falcon.Request.url
        try:
            raw_json = req.stream.read()
            print "POST RAW: ", raw_json
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Error',
                ex.message)

        try:
            result_json = json.loads(raw_json, encoding='utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Malformed JSON',
                'Could not decode the request body. The '
                'JSON was incorrect.')

        self.analyze_input(result_json)

        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(result_json, encoding='utf-8')

# falcon.API instances are callable WSGI apps
app = api = falcon.API()

# Resources are represented by long-lived class instances
things = ThingsResource()

# things will handle all requests to the '/things' URL path
api.add_route('/ldoper', things)
