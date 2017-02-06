#!/usr/bin/python 

from cmd2 import Cmd, make_option, options
from bigsuds import BIGIP, get_wsdls

class InvalidWSDLError(Exception):
    """Invalid WSDL error"""

class RegionItemNotFound(Exception):
    """Invalid WSDL error"""

class BigIPApp(Cmd, object):
    parse_qs = True

    __bigIPInstance = None
    __server = None
    __username = None
    __password = None
    __promptFormat = '\n[{0}@{1}]# '
    __defaultPrompt = '\nBIGIP# '

    __ispClasses = ['/Common/Telecom_address_New',
                    '/Common/Unicom_address_New',
                    '/Common/Mobile_address_New']

    __regions = [
		{'db_type': 'REGION_DB_TYPE_USER_DEFINED', 'name': '/Common/user_telecom'},
		{'db_type': 'REGION_DB_TYPE_USER_DEFINED', 'name': '/Common/user_mobile'},
		{'db_type': 'REGION_DB_TYPE_USER_DEFINED', 'name': '/Common/user_unicom'}
		]

    prompt = __defaultPrompt

    def do_help(self, args):
        print "\nDocumented commands (type help <topic>):"
        print "=========================================="
        cmds = ['findclass', 'list', 'add', 'delete', 'login', 'logout', 
		'listregion', 'findregion', 'deleteregion', 'addregion']

        def printHelp():
            cmdStr = ''
	
	    counter = 0
            for cmd in cmds:
                cmdStr += '%-8s' % cmd
		cmdStr += '\n'

            print cmdStr

        if not args.strip():
            printHelp()
        elif args.strip() not in cmds:
            printHelp()
        else:
            super(BigIPApp, self).do_help(args)

    @options([make_option('-w', '--wsdl', default='LocalLB', help="WSDL"),
              make_option('-m', '--netmask', help="Netmask"),
              make_option('-n', '--net', help="Network IP")])
    def do_findclass(self, args, opts=None):
        self.__assertLogged()
        print self.__findRule(opts.wsdl, opts.net, opts.netmask)

    @options([make_option('-w', '--wsdl', default='GlobalLB', help="WSDL"),
              make_option('-n', '--net', help="Network IP")])
    def do_findregion(self, args, opts=None):
        self.__assertLogged()
	try:
            name = self.__findRegion(opts.wsdl, opts.net)
	    print name
	except:
	    raise Exception('Can not find {%s}' % opts.net)

    @options([make_option('-w', '--wsdl', default='LocalLB', help="WSDL"),
              make_option('-i', '--isp', help="ISP name"),
              make_option('-m', '--netmask', help="Netmask"),
              make_option('-n', '--net', help="Network IP")])
    def do_add(self, args, opts=None):
        self.__assertLogged()
        try:
            self.__deleteRule(opts.wsdl, opts.net, opts.netmask)
            self.__addRule(opts.wsdl, opts.isp, opts.net, opts.netmask)
        except:
            if self.__findRule(opts.wsdl, opts.net, opts.netmask):
                raise Exception('Failed to delete existed rules')
            self.__addRule(opts.wsdl, opts.isp, opts.net, opts.netmask)

    @options([make_option('-w', '--wsdl', default='GlobalLB', help="WSDL"),
              make_option('-i', '--isp', help="ISP name"),
              make_option('-n', '--net', help="Network IP")])
    def do_addregion(self, args, opts=None):
        self.__assertLogged()
        try:
            self.__deleteRegion(opts.wsdl, opts.net)
            self.__addRegion(opts.wsdl, opts.isp, opts.net)
	except RegionItemNotFound:
            self.__addRegion(opts.wsdl, opts.isp, opts.net)
	except Exception as e:
	    print str(e)
	    raise Exception('Can not add region {%s}' % opts.net)

    @options([make_option('-w', '--wsdl', default='LocalLB', help="WSDL"),
              make_option('-m', '--netmask', help="Network Mask"),
              make_option('-n', '--net', help="Network IP")])
    def do_delete(self, args, opts=None):
        self.__assertLogged()
        self.__deleteRule(opts.wsdl, opts.net, opts.netmask)

    @options([make_option('-w', '--wsdl', default='GlobalLB', help="WSDL"),
              make_option('-n', '--net', help="Network IP")])
    def do_deleteregion(self, args, opts=None):
        self.__assertLogged()
	try:
            self.__deleteRegion(opts.wsdl, opts.net)
	except RegionItemNotFound:
	    pass
	except Exception as e:
	   print str(e)
	   raise Exception('Can not delete region {%s}' % opts.net)

    @options([make_option('-s', '--server', help="host name or ip"),
              make_option('-u', '--username', help="user name"),
              make_option('-p', '--password', help="user password")])
    def do_login(self, arg, opts=None):

        if self.__bigIPInstance:
            raise Exception('Logined already')

        if not opts.username:
            raise Exception('user name is required')

        if not opts.password:
            raise Exception('password is required')

        if not opts.server:
            raise Exception('server ip is required')

        self.__bigIPInstance = BIGIP(opts.server, opts.username, opts.password)
        self.__username = opts.username
        self.__password = opts.password
        self.__server = opts.server
        self.__updatePrompt()

    def do_logout(self, arg):
        self.__bigIPInstance = None
        self.prompt = self.__defaultPrompt

    @options([make_option('-w', '--wsdl', default='LocalLB', help="WSDL")])
    def do_list(self, arg, opts=None):
        self.__assertLogged()
        if opts.wsdl == 'LocalLB':
            allAddressClasses = self.__bigIPInstance.LocalLB.Class.get_address_class(self.__ispClasses)
        else:
            raise Exception('Invalid WSDL')

        for addressClass in allAddressClasses:
            print addressClass['name']
            for member in addressClass['members']:
                print '\tAddress: {0}\tNetmask: {1}'.format(member['address'], member['netmask'])

    @options([make_option('-w', '--wsdl', default='GlobalLB', help="WSDL")])
    def do_listregion(self, arg, opts=None):
        self.__assertLogged()
        if opts.wsdl == 'LocalLB':
            raise Exception('Invalid WSDL')
        else:
            regions = self.__getAllRegions(opts.wsdl)

        for region in regions:
            print region['name']
            for member in region['members']:
		for item in member:
                    print '\tAddress: {0}'.format(item['content'])

    def __assertLogged(self):
        if not self.__bigIPInstance:
            raise Exception('not logged')

        return True

    def __addRule(self, wsdl, isp, net, netmask):
        addressClass = {}
        addressClass['name'] = isp
        addressClass['members'] = [{'netmask': netmask, 'address': net}]
        self.__bigIPInstance.LocalLB.Class.add_address_class_member([addressClass])

    def __addRegion(self, wsdl, isp, net):
        if wsdl == 'LocalLB':
            raise InvalidWSDLError('Invalid WSDL')

        if isp is None:
            raise Exception('ISP is required')

	region = [{'db_type': 'REGION_DB_TYPE_USER_DEFINED', 'name': isp}]
	regionItem = [[{'content': net, 'negate': False, 'type': 'REGION_TYPE_CIDR'}]]
        self.__bigIPInstance.GlobalLB.Region.add_region_item(region, regionItem)

    def __deleteRule(self, wsdl, net, netmask):
        isp = self.__findRule(wsdl, net, netmask)
        if isp:
            if wsdl == 'LocalLB':
                deletedAddressClass = {}
                deletedAddressClass['name'] = isp
                deletedAddressClass['members'] = [{'netmask': netmask, 'address': net}]
                self.__bigIPInstance.LocalLB.Class.delete_address_class_member([deletedAddressClass])
            else:
                raise InvalidWSDLError('Invalid WSDL')
        else:
            raise Exception('Rule not existed')

    def __deleteRegion(self, wsdl, net):

        if not net:
            raise Exception('NetAddress is required')

        regionItem = self.__findRegionItem(wsdl, net)

        if regionItem:
            if wsdl == 'LocalLB':
                raise InvalidWSDLError('Invalid WSDL')
            else:
		region = [{'db_type': 'REGION_DB_TYPE_USER_DEFINED', 'name': regionItem['name']}]
		deletedItem = None
		for member in regionItem['members']:
		    for item in member:
			if item['content'] == net:
			    deletedItem = item

		if deletedItem:
                    self.__bigIPInstance.GlobalLB.Region.remove_region_item(region, [[deletedItem]])

    def __findRule(self, wsdl, net, netmask):
        addressClass = self.__findNetwork(wsdl, net, netmask)
        if addressClass:
            return addressClass['name']

        return None

    def __findRegion(self, wsdl, net):
	item = self.__findRegionItem(wsdl, net)
	return item['name']

    def __findRegionItem(self, wsdl, net):
        regions = self.__getAllRegions(wsdl)

        for region in regions:
            for member in region['members']:
		for item in member:
                    if item['content'] == net:
			return region

	raise RegionItemNotFound('null')

    def __getAllRegions(self, wsdl):
        if wsdl == 'LocalLB':
	    return
        else:
	    regionChains = []
            for region in self.__regions:
                regionChain = {}
                regionChain['name'] = region['name']
                regionChain['members'] = self.__bigIPInstance.GlobalLB.Region.get_region_item([region])
                regionChains.append(regionChain)
	
            return regionChains

    def __findNetwork(self, wsdl, net, netmask):
        if not wsdl:
            raise Exception('WSDL is required')

        if not net:
            raise Exception('Network is required')

        if not netmask:
            raise Exception('Netmask is required')

        if wsdl == 'LocalLB':
            allAddressClasses = self.__bigIPInstance.LocalLB.Class.get_address_class(self.__ispClasses)
        else:
            raise Exception('Invalid WSDL')

        for addressClass in allAddressClasses:

            for member in addressClass['members']:
                if member['netmask'] == netmask and member['address'] == net:
                    return addressClass

        return None

    def __updatePrompt(self):
        self.prompt = self.__promptFormat.format(self.__username,
                                                 self.__server)


app = BigIPApp()
app.cmdloop()
