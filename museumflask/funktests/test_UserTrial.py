# -*- coding: iso-8859-15 -*-
"""user_trial FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload
from funkload.utils import Data
#from funkload.utils import xmlrpc_get_credential

class UserTrial(FunkLoadTestCase):
    """XXX

    This test use a configuration file UserTrial.conf.
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

    def test_user_trial(self):
        # The description should be set in the configuration file
	server_url = 'http://193.61.36.71'
        # begin of test ---------------------------------------------

        # /tmp/tmpuF7zO4_funkload/watch0007.request
        #self.connect(server_url + "js.cloudflare.com:443",
        #    description="Connect cdnjs.cloudflare.com:443")
        # /tmp/tmpuF7zO4_funkload/watch0014.request
        self.get("http://193.61.36.71/browseproperties",
            description="Get /browseproperties")
        # /tmp/tmpuF7zO4_funkload/watch0017.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0019.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0022.request
        # /tmp/tmpuF7zO4_funkload/watch0024.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.wiki.452",
            description="Get /Museum/nid/n0/mm.wiki.452")
        # /tmp/tmpuF7zO4_funkload/watch0026.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.mald.066",
            description="Get /Museum/nid/n0/mm.mald.066")
        # /tmp/tmpuF7zO4_funkload/watch0027.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.mald.082",
            description="Get /Museum/nid/n0/mm.mald.082")
        # /tmp/tmpuF7zO4_funkload/watch0028.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.wiki.309",
            description="Get /Museum/nid/n0/mm.wiki.309")
        # /tmp/tmpuF7zO4_funkload/watch0029.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.wiki.049",
            description="Get /Museum/nid/n0/mm.wiki.049")
        # /tmp/tmpuF7zO4_funkload/watch0030.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.misc.165",
            description="Get /Museum/nid/n0/mm.misc.165")
        # /tmp/tmpuF7zO4_funkload/watch0031.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.misc.073",
            description="Get /Museum/nid/n0/mm.misc.073")
        # /tmp/tmpuF7zO4_funkload/watch0032.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.domus.SE149",
            description="Get /Museum/nid/n0/mm.domus.SE149")
        # /tmp/tmpuF7zO4_funkload/watch0033.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.domus.YH147",
            description="Get /Museum/nid/n0/mm.domus.YH147")
        # /tmp/tmpuF7zO4_funkload/watch0034.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.aim.0679",
            description="Get /Museum/nid/n0/mm.aim.0679")
        # /tmp/tmpuF7zO4_funkload/watch0035.request
        self.get("http://193.61.36.71/search",
            description="Get /search")
        # /tmp/tmpuF7zO4_funkload/watch0036.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0037.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Postcode'],
            ['condition', 'match'],
            ['matchstring', 'sg1'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0039.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Postcode'],
            ['condition', 'match'],
            ['matchstring', 'sg1'],
            ['coltomatch', 'Accreditation'],
            ['condition', 'match'],
            ['matchstring', 'Unaccredited'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0040.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Postcode'],
            ['condition', 'match'],
            ['matchstring', 'sg1'],
            ['coltomatch', 'Accreditation'],
            ['condition', 'match'],
            ['matchstring', 'Unaccredited'],
            ['multiselect[]', 'MM_size']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0046.request
        # /tmp/tmpuF7zO4_funkload/watch0047.request
        self.get("http://193.61.36.71/search",
            description="Get /search")
        # /tmp/tmpuF7zO4_funkload/watch0048.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0049.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Sea_and_seafaring'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0051.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Sea_and_seafaring'],
            ['coltomatch', 'Year_opened'],
            ['condition', 'LT'],
            ['matchstring', '2013'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0052.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Sea_and_seafaring'],
            ['coltomatch', 'Year_opened'],
            ['condition', 'PGT'],
            ['matchstring', '2013'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0054.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.musa.162",
            description="Get /Museum/nid/n0/mm.musa.162")
        # /tmp/tmpuF7zO4_funkload/watch0055.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.musa.162",
            description="Get /Museum/nid/n0/mm.musa.162")
        # /tmp/tmpuF7zO4_funkload/watch0056.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.domus.SE571",
            description="Get /Museum/nid/n0/mm.domus.SE571")
        # /tmp/tmpuF7zO4_funkload/watch0057.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.aim.0566",
            description="Get /Museum/nid/n0/mm.aim.0566")
        # /tmp/tmpuF7zO4_funkload/watch0058.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.aim.0598",
            description="Get /Museum/nid/n0/mm.aim.0598")
        # /tmp/tmpuF7zO4_funkload/watch0059.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.mald.163",
            description="Get /Museum/nid/n0/mm.mald.163")
        # /tmp/tmpuF7zO4_funkload/watch0060.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.misc.123",
            description="Get /Museum/nid/n0/mm.misc.123")
        # /tmp/tmpuF7zO4_funkload/watch0061.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.aim.1093",
            description="Get /Museum/nid/n0/mm.aim.1093")
        # /tmp/tmpuF7zO4_funkload/watch0062.request
        self.get("http://193.61.36.71/Museum/nid/n0/mm.aim.1267",
            description="Get /Museum/nid/n0/mm.aim.1267")
        # /tmp/tmpuF7zO4_funkload/watch0063.request
        self.get("http://193.61.36.71/visualisations",
            description="Get /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0067.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0068.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/All%3Fid%3D'menuviz-1-1-1%3AAll'%26name%3D'All'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0069.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Location%3Fid%3D'menuviz-1-1-1%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0070.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Location/England%3Fid%3D'menuviz-1-1-1-3%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0071.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Location/England/East_Midlands%3Fid%3D'menuviz-1-1-1-3-2%3AEast%20Midlands'%26name%3D'East%20Midlands'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0072.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Location/England/East_Midlands/Leicestershire%3Fid%3D'menuviz-1-1-1-3-2-1%3ALeicestershire'%26name%3D'Leicestershire'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0073.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Location/England/East_Midlands/Lincolnshire%3Fid%3D'menuviz-1-1-1-3-2-1%3ALincolnshire'%26name%3D'Lincolnshire'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0074.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/Location/England/East_Midlands/Nottinghamshire%3Fid%3D'menuviz-1-1-1-3-2-1%3ANottinghamshire'%26name%3D'Nottinghamshire'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0076.request
        self.post("http://update.googleapis.com/service/update2?cup2key=7:1189934218&cup2hreq=53b73c4fcede6027b533ce02ad8bbe5f0353c5795e068ae5e9319554503b801f", Data('application/xml', '''<?xml version="1.0" encoding="UTF-8"?><request protocol="3.1" dedup="cr" acceptformat="crx2,crx3" sessionid="{1bf8e6c2-f897-493f-93a0-7fbf6997e499}" requestid="{7563a1c1-8102-437a-a185-3917363729cf}" version="chrome-66.0.3359.181" prodversion="66.0.3359.181" lang="en-GB" updaterchannel="Built on Ubuntu , running on Ubuntu 16.04" prodchannel="Built on Ubuntu , running on Ubuntu 16.04" os="linux" arch="x64" nacl_arch="x86-64"><hw physmemory="16"/><os platform="Linux" arch="x86_64" version="4.4.0-127-generic"/><app appid="gcmjkmgdlgnkkcocmoeiminaijmmjnii" version="7.54" cohort="1:bm1:" cohortname="M54AndAbove" enabled="1"><updatecheck/><ping rd="4181" ping_freshness="{bceaef53-04c7-45c1-b218-5aae6e892027}"/><packages><package fp="1.eaa293e9c8efa4d5c4243d6dfea82244d6bb0d03c3a8423f9431eaf9f7a6425e"/></packages></app><app appid="hfnkpimlhhgieaddgfemjhofmfblmnib" version="4514" cohort="1:jcl:" cohortname="Auto" enabled="1"><updatecheck/><ping rd="4181" ping_freshness="{d873163c-d33f-40c3-a4be-2e2619f31932}"/><packages><package fp="1.d6a6a2e8150f04bb105bb09b22059b6213fe7257d810027de54f23c4d3c278dc"/></packages></app><app appid="ojjgnpkioondelmggbekfhllhdaimnho" version="780" cohort="1:0:" cohortname="Auto" enabled="1"><updatecheck/><ping rd="4181" ping_freshness="{aca5a91f-6746-4615-8956-06bbbe5995b0}"/><packages><package fp="1.7619bca65da5cadd9acab9f03d125a2439ab99d0d92fab913480848df0452e2c"/></packages></app><app appid="llkgjffcdpffmhiakmfcdcblohccpfmo" version="0.0.0.0" enabled="1"><updatecheck/><ping rd="4181" ping_freshness="{40f3db54-7eaa-4a7f-8433-170e3766e9cd}"/></app><app appid="khaoiebndkojlmppeemjhbpbandiljpe" version="16" cohort="1:cux:" cohortname="Auto" enabled="1"><updatecheck/><ping rd="4181" ping_freshness="{e436adad-4099-4b46-8118-916b4e7d9e35}"/><packages><package fp="1.4c2082ae35561afe17152a7a33c946502380962bcf29d6af82e8c3e868fe6fd4"/></packages></app><app appid="giekcmmlnklenlaomppkphknjmnnpneh" version="4" cohort="1:j5l:" cohortname="Auto" enabled="1"><updatecheck/><ping rd="4181" ping_freshness="{c13b8954-6df4-4f18-b9cd-90da5fd9f92a}"/><packages><package fp="1.3e0bc577e6a70f1ee3aea6e88b1d6e9390695692881a998f4c0e3c6d7cab7ad5"/></packages></app><app appid="aemomkdncapdnfajjbbcbdebjljbpmpj" version="1.0.3.0" enabled="1"><updatecheck/><ping rd="4181" ping_freshness="{05b0d454-d5f2-42a3-8535-71a96ba1d413}"/><packages><package fp="1.a5b2393f31f7d478f003a2923b91af8a8fd94d7bc7d5fad2e290b0c47141ca3b"/></packages></app></request>'''),
            description="Post /service/update2")
        # /tmp/tmpuF7zO4_funkload/watch0077.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_at_a_given_time/MM_size%3Fid%3D'menuviz-1-1-1%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0079.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Governance%3Fid%3D'menuviz-1-1-3%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0080.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Governance/Government%3Fid%3D'menuviz-1-1-3-7%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0081.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Governance/Independent%3Fid%3D'menuviz-1-1-3-7%3AIndependent'%26name%3D'Independent'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0082.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Location%3Fid%3D'menuviz-1-1-3%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0083.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Location/England%3Fid%3D'menuviz-1-1-3-9%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0084.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Location/England/London%3Fid%3D'menuviz-1-1-3-9-6%3ALondon'%26name%3D'London'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0085.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Location/England/South_West%3Fid%3D'menuviz-1-1-3-9-6%3ASouth%20West'%26name%3D'South%20West'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0086.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/open_over_time/Location/England/South_West/Devon%3Fid%3D'menuviz-1-1-3-9-6-22%3ADevon'%26name%3D'Devon'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0087.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Governance%3Fid%3D'menuviz-1-1-4%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0088.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Governance/Government%3Fid%3D'menuviz-1-1-4-10%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0089.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Classification_2018%3Fid%3D'menuviz-1-1-4%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0090.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Classification_2018/Arts%3Fid%3D'menuviz-1-1-4-11%3AArts'%26name%3D'Arts'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0091.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Classification_2018/Personality%3Fid%3D'menuviz-1-1-4-11%3APersonality'%26name%3D'Personality'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0092.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Classification_2018/Personality%3Fid%3D'menuviz-1-1-4-11%3APersonality'%26name%3D'Personality'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0093.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Classification_2018/Science_and_technology%3Fid%3D'menuviz-1-1-4-11%3AScience_and_technology'%26name%3D'Science_and_technology'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0094.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Location%3Fid%3D'menuviz-1-1-4%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0095.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/openings_over_time/Location/England%3Fid%3D'menuviz-1-1-4-12%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0096.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/All%3Fid%3D'menuviz-1-1-5%3AAll'%26name%3D'All'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0097.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/All%3Fid%3D'menuviz-1-1-5%3AAll'%26name%3D'All'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0098.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Governance%3Fid%3D'menuviz-1-1-5%3AGovernance'%26name%3D'Governance'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0099.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Governance/Government%3Fid%3D'menuviz-1-1-5-13%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0100.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Governance/Independent%3Fid%3D'menuviz-1-1-5-13%3AIndependent'%26name%3D'Independent'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0101.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Classification_2018%3Fid%3D'menuviz-1-1-5%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0102.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Classification_2018/Leisure_and_sport%3Fid%3D'menuviz-1-1-5-14%3ALeisure_and_sport'%26name%3D'Leisure_and_sport'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0103.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/MM_size%3Fid%3D'menuviz-1-1-5%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0104.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Location%3Fid%3D'menuviz-1-1-5%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0105.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Location/England%3Fid%3D'menuviz-1-1-5-15%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0106.request
        self.get("http://193.61.36.71/visualisations/Visualisations/Number_of_museums/closings_over_time/Location/England/East_Midlands%3Fid%3D'menuviz-1-1-5-15-10%3AEast%20Midlands'%26name%3D'East%20Midlands'%26class%3D'node'%26location%3D'UK'",
            description="Get /visualisations/Vis...'%26location%3D'UK'")
        # /tmp/tmpuF7zO4_funkload/watch0109.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Governance/Government'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018/Belief_and_identity'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-16%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8-20%3ABelief_and_identity'%26name%3D'Belief_and_identity'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-16%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0110.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Governance/Government'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018/Archaeology'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-16%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8-20%3AArchaeology'%26name%3D'Archaeology'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8-20%3AArchaeology'%26name%3D'Archaeology'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0111.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Governance/Government'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-16%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0112.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Governance/Government'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-16%3AGovernment'%26name%3D'Government'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0113.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/UK'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0114.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0115.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/East Midlands'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12%3AEast%20Midlands'%26name%3D'East%20Midlands'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12%3AEast%20Midlands'%26name%3D'East%20Midlands'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0116.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/East Midlands/Lincolnshire'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12-41%3ALincolnshire'%26name%3D'Lincolnshire'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12-41%3ALincolnshire'%26name%3D'Lincolnshire'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0117.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/East Midlands/Nottinghamshire'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12-41%3ANottinghamshire'%26name%3D'Nottinghamshire'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12-41%3ANottinghamshire'%26name%3D'Nottinghamshire'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0118.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/London'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/MM_size'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12%3ALondon'%26name%3D'London'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AMM_size'%26name%3D'MM_size'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12%3ALondon'%26name%3D'London'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0120.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/London'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12%3ALondon'%26name%3D'London'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0121.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18%3AEngland'%26name%3D'England'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0122.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/UK'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0123.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/UK'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7%3ALocation'%26name%3D'Location'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0124.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/East Midlands/Derbyshire'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12-41%3ADerbyshire'%26name%3D'Derbyshire'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12-41%3ADerbyshire'%26name%3D'Derbyshire'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0125.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/London'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12%3ALondon'%26name%3D'London'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12%3ALondon'%26name%3D'London'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0126.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/North West'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12%3ANorth%20West'%26name%3D'North%20West'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12%3ANorth%20West'%26name%3D'North%20West'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0127.request
        self.post("http://193.61.36.71/visualisations", params=[
            ['colorscheme-label', '#219264'],
            ['xaxisselect-label', '/Visualisations/Plot/X/Location/England/South East'],
            ['yaxisselect-label', '/Visualisations/Plot/Y/Classification_2018'],
            ['xaxisselect-dict', "%3Fid%3D'menuviz-1-2-7-18-12%3ASouth%20East'%26name%3D'South%20East'%26class%3D'node'%26location%3D'UK'"],
            ['yaxisselect-dict', "%3Fid%3D'menuviz-1-2-8%3AClassification_2018'%26name%3D'Classification_2018'%26class%3D'node'%26location%3D'UK'"],
            ['contextdict', "%3Fid%3D'menuviz-1-2-7-18-12%3ASouth%20East'%26name%3D'South%20East'%26class%3D'node'%26location%3D'UK'"]],
            description="Post /visualisations")
        # /tmp/tmpuF7zO4_funkload/watch0128.request
        self.get("http://193.61.36.71/browseproperties",
            description="Get /browseproperties")
        # /tmp/tmpuF7zO4_funkload/watch0129.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0130.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0131.request
        self.get("http://193.61.36.71/search",
            description="Get /search")
        # /tmp/tmpuF7zO4_funkload/watch0132.request
        self.get("http://193.61.36.71/api/datasetversion/get",
            description="Get /api/datasetversion/get")
        # /tmp/tmpuF7zO4_funkload/watch0133.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts-Ceramics'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0135.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts-Ceramics'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'LT'],
            ['matchstring', '1980'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0136.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts-Ceramics'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1980'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0137.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts-Ceramics'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1980'],
            ['coltomatch', 'Visitor_Numbers_Data'],
            ['condition', 'NEQ'],
            ['matchstring', '0'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0138.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1980'],
            ['coltomatch', 'Visitor_Numbers_Data'],
            ['condition', 'NEQ'],
            ['matchstring', '0'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0139.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1980'],
            ['coltomatch', 'Visitor_Numbers_Data'],
            ['condition', 'GT'],
            ['matchstring', '1000'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0140.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1980'],
            ['coltomatch', 'Visitor_Numbers_Data'],
            ['condition', 'GT'],
            ['matchstring', '1000'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0141.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Arts'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1980'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0142.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Buildings'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1980'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0143.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Classification_2018'],
            ['condition', 'match'],
            ['matchstring', 'Buildings'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1960'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0144.request
        self.get("http://193.61.36.71/api/geoadmin/get/e",
            description="Get /api/geoadmin/get/e")
        # /tmp/tmpuF7zO4_funkload/watch0145.request
        self.get("http://193.61.36.71/api/geoadmin/get/en",
            description="Get /api/geoadmin/get/en")
        # /tmp/tmpuF7zO4_funkload/watch0146.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Admin_Area'],
            ['condition', 'EQ'],
            ['matchstring', 'England'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1960'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0147.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Admin_Area'],
            ['condition', 'EQ'],
            ['matchstring', 'England'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1960'],
            ['coltomatch', 'Visitor_Numbers_Data'],
            ['condition', 'LT'],
            ['matchstring', '20000'],
            ['multiselect[]', 'Default']],
            description="Post /search")
        # /tmp/tmpuF7zO4_funkload/watch0149.request
        self.post("http://193.61.36.71/search", params=[
            ['coltomatch', 'Admin_Area'],
            ['condition', 'EQ'],
            ['matchstring', 'England'],
            ['coltomatch', 'Governance_Change'],
            ['condition', 'GT'],
            ['matchstring', '1960'],
            ['coltomatch', 'Visitor_Numbers_Data'],
            ['condition', 'GT'],
            ['matchstring', '20'],
            ['multiselect[]', 'Default']],
            description="Post /search")

        # end of test -----------------------------------------------

    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
