# -*- coding: iso-8859-15 -*-
"""basic_navigation FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload
from funkload.utils import Data
#from funkload.utils import xmlrpc_get_credential

class BasicNavigation(FunkLoadTestCase):
    """XXX

    This test use a configuration file BasicNavigation.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.logd("setUp")
        self.server_url = self.conf_get('main', 'url')
        # XXX here you can setup the credential access like this
        # credential_host = self.conf_get('credential', 'host')
        # credential_port = self.conf_getInt('credential', 'port')
        # self.login, self.password = xmlrpc_get_credential(credential_host,
        #                                                   credential_port,
        # XXX replace with a valid group
        #                                                   'members')

    def test_basic_navigation(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------

        # /tmp/tmpJK6ViQ_funkload/watch0026.request
        self.get(server_url + "/visualisations",
            description="Get /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0046.request
        self.get(server_url + "/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpJK6ViQ_funkload/watch0048.request
        self.get(server_url + "/static/favicon.ico",
            description="Get /static/favicon.ico")
        # /tmp/tmpJK6ViQ_funkload/watch0049.request
        self.get(server_url + "/browseproperties",
            description="Get /browseproperties")
        # /tmp/tmpJK6ViQ_funkload/watch0058.request
        self.get(server_url + "/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpJK6ViQ_funkload/watch0060.request
        self.get(server_url + "/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpJK6ViQ_funkload/watch0087.request
        self.get(server_url + "/Museum/nid/n0/mm.domus.SE118",
            description="Get /Museum/nid/n0/mm.domus.SE118")
        # /tmp/tmpJK6ViQ_funkload/watch0088.request
        self.get(server_url + "/Museum/nid/n0/mm.domus.WA095",
            description="Get /Museum/nid/n0/mm.domus.WA095")
        # /tmp/tmpJK6ViQ_funkload/watch0089.request
        self.get(server_url + "/Museum/nid/n0/mm.domus.SE499",
            description="Get /Museum/nid/n0/mm.domus.SE499")
        # /tmp/tmpJK6ViQ_funkload/watch0090.request
        self.get(server_url + "/Museum/nid/n0/mm.domus.YH001",
            description="Get /Museum/nid/n0/mm.domus.YH001")
        # /tmp/tmpJK6ViQ_funkload/watch0091.request
        self.get(server_url + "/Museum/nid/n0/mm.domus.NW036",
            description="Get /Museum/nid/n0/mm.domus.NW036")
        # /tmp/tmpJK6ViQ_funkload/watch0092.request
        self.get(server_url + "/Museum/nid/n0/mm.wiki.254",
            description="Get /Museum/nid/n0/mm.wiki.254")
        # /tmp/tmpJK6ViQ_funkload/watch0153.request
        self.get(server_url + "/search",
            description="Get /search")
        # /tmp/tmpJK6ViQ_funkload/watch0156.request
        self.get(server_url + "/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpJK6ViQ_funkload/watch0159.request
        self.post(server_url + "/search", params=[
            ['coltomatch', 'Name_of_museum'],
            ['condition', 'match'],
            ['matchstring', 'medical'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpJK6ViQ_funkload/watch0183.request
        self.post(server_url + "/search", params=[
            ['coltomatch', 'Name_of_museum'],
            ['condition', 'match'],
            ['matchstring', 'medical'],
            ['coltomatch', 'MM_size'],
            ['condition', 'match'],
            ['matchstring', 'small'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpJK6ViQ_funkload/watch0184.request
        self.post(server_url + "/search", params=[
            ['coltomatch', 'Name_of_museum'],
            ['condition', 'match'],
            ['matchstring', 'medical'],
            ['coltomatch', 'MM_size'],
            ['condition', 'match'],
            ['matchstring', 'medium'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpJK6ViQ_funkload/watch0185.request
        self.post(server_url + "/search", params=[
            ['coltomatch', 'Name_of_museum'],
            ['condition', 'match'],
            ['matchstring', 'medical'],
            ['coltomatch', 'MM_size'],
            ['condition', 'match'],
            ['matchstring', 'large'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpJK6ViQ_funkload/watch0186.request
        self.post(server_url + "/search", params=[
            ['coltomatch', 'Name_of_museum'],
            ['condition', 'match'],
            ['matchstring', 'medical'],
            ['coltomatch', 'MM_size'],
            ['condition', 'match'],
            ['matchstring', 'unknown'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpJK6ViQ_funkload/watch0187.request
        self.post(server_url + "/search", params=[
            ['coltomatch', 'Name_of_museum'],
            ['condition', 'match'],
            ['matchstring', 'medical'],
            ['coltomatch', 'MM_size'],
            ['condition', 'match'],
            ['matchstring', 'unknown'],
            ['coltomatch', 'Postcode'],
            ['condition', 'match'],
            ['matchstring', 'rg6'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpJK6ViQ_funkload/watch0188.request
        self.post(server_url + "/search", params=[
            ['coltomatch', 'Name_of_museum'],
            ['condition', 'match'],
            ['matchstring', 'medical'],
            ['coltomatch', 'MM_size'],
            ['condition', 'match'],
            ['matchstring', 'unknown'],
            ['coltomatch', 'Postcode'],
            ['condition', 'match'],
            ['matchstring', 'rg'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpJK6ViQ_funkload/watch0190.request
        self.get(server_url + "/visualisations",
            description="Get /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0191.request
        self.get(server_url + "/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpJK6ViQ_funkload/watch0192.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/All%3Fid%3D'menuviz-1-1-1%3AAll'%26name%3D'All'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0193.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Governance%3Fid%3D'menuviz-1-1-1%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0194.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Governance/Government%3Fid%3D'menuviz-1-1-1-1%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0195.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Governance/Independent%3Fid%3D'menuviz-1-1-1-1%3AIndependent'%26name%3D'Independent'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0196.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Classification_2018%3Fid%3D'menuviz-1-1-1%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0197.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Classification_2018/Arts%3Fid%3D'menuviz-1-1-1-2%3AArts'%26name%3D'Arts'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0198.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Classification_2018/Belief_and_identity%3Fid%3D'menuviz-1-1-1-2%3ABelief_and_identity'%26name%3D'Belief_and_identity'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0199.request
        self.post(server_url + "/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/MM_size'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Governance'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0200.request
        self.post(server_url + "/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/MM_size'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Governance/Government'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8-19%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8-19%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0201.request
        self.post(server_url + "/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/MM_size'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Governance/Independent'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8-19%3AIndependent'%26name%3D'Independent'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8-19%3AIndependent'%26name%3D'Independent'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0202.request
        self.post(server_url + "/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Classification_2018'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Governance/Independent'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8-19%3AIndependent'%26name%3D'Independent'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0203.request
        self.post(server_url + "/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Classification_2018'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Governance'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0204.request
        self.post(server_url + "/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Classification_2018'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpJK6ViQ_funkload/watch0205.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_over_time/Classification_2018%3Fid%3D'menuviz-1-1-3%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0206.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_over_time/Classification_2018/Archaeology%3Fid%3D'menuviz-1-1-3-8%3AArchaeology'%26name%3D'Archaeology'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpJK6ViQ_funkload/watch0207.request
        self.get(server_url + "/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Classification_2018/Personality%3Fid%3D'menuviz-1-1-1-2%3APersonality'%26name%3D'Personality'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")

        # end of test -----------------------------------------------

    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
