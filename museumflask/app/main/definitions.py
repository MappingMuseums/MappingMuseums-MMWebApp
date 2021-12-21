##
# @file
#  
#  This module implements all strings used in the code as well as lookup
#  dictionaries,lists and file names. Used globally and is paramount for
#  the column indirection. This way a column can change name in the sheet
#  and you change the name here once and it works again.
#  
#  
#  
#  
#  
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import os


MAINSHEET="main"

##  datatype naming definitions
HASNAME			    = "has"
DEFRANGE		    = "defRange"
DEFCLASS		    = "defClass"
DEFNAME			    = "def"
RANGENAME		    = "Range"
LISTNAME		    = "List"

##  datatypes definitions for the abstract types
PROPERTY_TYPES_DICT={}
DEFINED_TYPES="HierType","ListType","RangeType"
DEFINED_RANGETYPE=DEFINED_TYPES[2]
DEFINED_LISTTYPE=DEFINED_TYPES[1]
DEFINED_HIERTYPE=DEFINED_TYPES[0]
RANGE_SEPARATOR=":"
HIER_SEPARATOR="/"
HIER_SUBCLASS_SEPARATOR="-"
HIER_SUBCLASS_VIEW_SEPARATOR=":"
RANGE_OPEN="9999:9999"

XSD_STRINGTYPE='xsd:string'
##  xmldatatypes definitions for the xsd types
XML_TYPES=['string','integer','positiveInteger','date','boolean','decimal'];
XML_TYPES_WITH_PREFIX=[XSD_STRINGTYPE,'xsd:integer','xsd:positiveInteger','xsd:date','xsd:boolean','xsd:decimal'];
XML_TYPES_PREFIX="xsd:"

##  lists definitions for lists of predicates and types and configurations
LISTS={}
LISTS_VALUES={}
RESET_LISTS={}
RESET_LISTS_VALUES={}
RESET_NAME="Reset"

##  dicts dictionaries for the types
LISTITEMS  = []
ATTRITYPES = []
DATAGROUPS = []

ONTOLISTS=['DataTypeList','PredicateList']
DATATYPEDICT  = {}



CONFIGTREES= {}
CONFIGTREEITEMS  = []

##  search definitions and dictionaries for the search facility
DEFAULT_SEARCH_SHOW_COLUMNS = []
DEFAULT_SEARCH_SHOW_COLUMNS_NAME = 'DEFAULT_SEARCH_SHOW_COLUMNS'

DEFAULT_SEARCH_FILTER_COLUMNS = []
DEFAULT_SEARCH_FILTER_COLUMNS_NAME = 'DEFAULT_SEARCH_FILTER_COLUMNS'

DEFAULT_VIEW_ALL_COLUMNS      = []
DEFAULT_VIEW_ALL_COLUMNS_NAME = 'DEFAULT_VIEW_ALL_COLUMNS'


# This determines if an item in the LISTITEMS is configurable as opposed to the LIST TYPE of items like governance
# VARIABLES like the above search columns should be named DEFAULT_ and property
NAMED_CONFIGURABLE_PROPERTIES=['DEFAULT_']

##  ONS dictionaries for the processing of ONS data
POSTCODE2_DISTR_DICT={}
POSTCODE2_COUNTY_DICT={}
POSTCODE2_COUNTRY_DICT={}
POSTCODE2_LA_DICT={}
POSTCODE2_REGION_DICT={}
COUNTY2_REGION_DICT={}
LA2_COUNTY_DICT={}
LA2_REGION_DICT={}

##  BASEDIR where files are stored
BASEDIR = os.path.abspath(os.path.dirname(__file__))
BASEDIR=BASEDIR.replace("app/main","json/")

##  column Column definitions.
GEOCOL                      = "Geocol"
GEOADMCOL                   = "GeoAdmcol"
GEOADMNAME                  = "geoadmname"
DOMUS_SUBJECTCLASSIFICATION = "DOMUS_Subject_Matter"
NAME_OF_MUSEUM		    = "Name_of_museum"
LATITUDE		    = "Latitude"
LONGITUDE		    = "Longitude"
SUBJECT_MATTER		    = "Subject_Matter"
SIZE		            = "Size"
ACCREDITATION		    = "Accreditation"
GOVERNANCE		    = "Governance"
PROJECT_ID		    = "project_id"
POSTCODE		    = "Postcode"
COUNTY			    = "County"
YEAR_OPENED	            = "Year_opened"
YEAR_CLOSED	            = "Year_closed"
YEAR_EXISTS                 = "Year_exists"
YEAR_OF_FOUNDATION	    = "Year_of_foundation"
ADDRESS_LINE_1		    = "Address_line_1"
ADDRESS_LINE_2		    = "Address_line_2"
ADDRESS_LINE_3		    = "Address_line_3"
TOWNORCITY		    = "Town_or_City"
GREY_AREA		    = "Grey_area"
NOTES			    = "Notes"
VISITORNUMBERS              = "Visitor_Numbers_Data"
STATUSCHANGE                = "Governance_Change"

## Deprivation and output area
GROUP_NAME                  = "Geodemographic_group"
SUPERGROUP_NAME_LONG        = "Geodemographic_supergroup_name_long"
GROUP_CODE                  = "Geodemographic_group_code"
SUBGROUP_NAME               = "Geodemographic_subgroup"
GROUP_NAME_LONG             = "Geodemographic_group_name_long"
SUBGROUP_NAME_LONG          = "Geodemographic_subgroup_name_long"
SUBGROUP_CODE		        = "Geodemographic_subgroup_code"


DEPRIVATION_INDEX	         = "Deprivation_index"
DEPRIVATION_INDEX_INCOME     = "Deprivation_index_income"
DEPRIVATION_INDEX_EMPLOYMENT = "Deprivation_index_employment"
DEPRIVATION_INDEX_EDUCATION  = "Deprivation_index_education"
DEPRIVATION_INDEX_HEALTH     = "Deprivation_index_health"
DEPRIVATION_INDEX_CRIME	     = "Deprivation_index_crime"
DEPRIVATION_INDEX_HOUSING    = "Deprivation_index_housing"
DEPRIVATION_INDEX_SERVICES   = "Deprivation_index_services"




## rdf uri definitions
RDFDATAURI		            = 'bbk.ac.uk/MuseumMapProject/data/'
RDFDEFURI		            = 'bbk.ac.uk/MuseumMapProject/def/'
RDFDEFURI_NOENDINGSLASH	    = 'bbk.ac.uk/MuseumMapProject/def'
HTTPSTRING                  = 'http://'
PREFIX                      ='bbkmm'
PREFIX_WITHCOLON            ='bbkmm:'



JSONDATA_FILES = {
    "county":"Counties_withmuseumfreq_2016.geojson",
    "localauth":"localauthdistrictdata_withmuseumfreq_16.geojson",
    "region":"Regions_withmuseumfreq_2016.geojson",
    "country":"Countries_withmuseumfreq_2016.geojson",
    "combauth":"CA_withmuseumfreq_2017.geojson"
    }   

JSONDATA ={}   

RDF_PREFIX_PRELUDE="""

    prefix dcterms:         <http://purl.org/dc/terms/>  
    prefix owl:             <http://www.w3.org/2002/07/owl#> 
    prefix rdf:             <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs:            <http://www.w3.org/2000/01/rdf-schema#>  
    prefix xml:             <http://www.w3.org/XML/1998/namespace> 
    prefix xsd:             <http://www.w3.org/2001/XMLSchema#>
    prefix prov:            <http://www.w3.org/ns/prov#>
    prefix time:            <http://www.w3.org/2006/time#>
    """

MENU_BASE="#MENU#"
PATH_BASE="${PATH}"

DATASETVERSION=None

SPARQL_KEYWORDS= [ "SELECT",
		   "ORDER",
		   "GRAPH",
		   "PREFIX",
		   "CONSTRUCT",
		   "LIMIT",
		   "FROM",
		   "OPTIONAL",
		   "DESCRIBE",
		   "OFFSET",
		   "WHERE",
		   "UNION",
		   "ASK",
		   "DISTINCT",
		   "FILTER",
		   "DATATYPE",
		   "REGEX",
		   "BOUND" ]
