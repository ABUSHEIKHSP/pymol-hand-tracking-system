import xmlrpc.client

pymol = xmlrpc.client.ServerProxy("http://localhost:9123")

pymol.do("zoom center, 30")