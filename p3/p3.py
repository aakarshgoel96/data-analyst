
# coding: utf-8

# # Data Wrangling with MongoDB
# 
# ### OpenStreetMap Sample Project
# 
# #### Map Area: Honolulu, Hawaii, United States
# 
# http://www.openstreetmap.org/#map=10/21.4860/-157.9710
# 
# 

# In[135]:

#importing all necessary files
import os
import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re
import codecs
import json
import string
from pymongo import MongoClient


# In[136]:

#Fetching osm data in python variable map_data
datadir = ""
datafile = "honolulu_hawaii.osm"
map_data = os.path.join(datadir, datafile)


# ##  Problems Encountered in the Map(Auditing)

# In[137]:

##iterative parsing using Element tree to process the map file and find out what tags are there
def count_tags(filename):
        tags = {}
        for event, elem in ET.iterparse(filename):
            if elem.tag in tags: 
                tags[elem.tag] += 1
            else:
                tags[elem.tag] = 1
        return tags
map_tags = count_tags(map_data)
pprint.pprint(map_tags)


# Here we founded that there are 242190 nodes, 117607 tags, 25500 ways and 384 relation.

# In[138]:

#people invovlved in the map editing.
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        for e in element:
            if 'uid' in e.attrib:
                users.add(e.attrib['uid'])
    return users
users = process_map(map_data)
len(users)


# In[139]:

lower = re.compile(r'^([a-z]|_)*$')                    # Regular Expressions for different cases matching
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# >These expressions are used for validating a string in particular format. 

# In[140]:

# initial expected street names
expected = ["Street", "Avenue", "Boulevard","Broadway","Drive", "Court", "Place", "Square", "Lane",
            "Road", "Trail", "Parkway"]


# >Initially we consider some common words as expected street names.

# In[141]:

#Finding counts for different tag categories
def key_type(element, keys):                  
    if element.tag == "tag":
        for tag in element.iter('tag'):
            k = tag.get('k')
            if lower.search(k):
                keys['lower'] += 1
            elif lower_colon.search(k):
                keys['lower_colon'] += 1
            elif problemchars.search(k):
                keys['problemchars'] += 1
                print tag.get('k')
            else:
                keys['other'] += 1
    return keys

 #Distributing in different categories and finding tag count
def process_map(filename):                     
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}  
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

map_keys = process_map(map_data)
pprint.pprint(map_keys)


# 
# 
#    > For the function: key_type & process_map. We check the "k" value for each 
# 
#    > For the function 'key_type', we have a count of each of three tag categories in a dictionary: "lower", for tags that contain only lowercase letters and are valid, "lower_colon", for otherwise valid tags with a colon in their names, "problemchars", for tags with problematic characters, and
# 
# 

# ### Auditing Problems associating with street name abbreviations

# In[142]:

def audit_street_type(street_types, street_name):    # add unexpected street name to a list
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def is_street_name(elem):
    # determine whether a element is a street name
    return (elem.attrib['k'] == "addr:street")

def audit_street(osmfile):
    # iter through all street name tag under node or way and audit the street name value
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

st_types = audit_street(map_data)
# print out unexpected street names
pprint.pprint(dict(st_types))


# >We found that lot of abbreviations are used in the street names.
# 
# >So some fix of names is required for that which can be done by mapping abbreviations to their full form.

# In[143]:

mapping={  'Ave'  : 'Avenue',             #mapping abbreviations to their full form
           'Ave.' : 'Avenue',
           'Apt'  : 'Apartment',
           'Blvd' : 'Boulevard',
           'Dr'   : 'Drive',
           'Ln'   : 'Lane',
           'Pkwy' : 'Parkway',
           'Rd'   : 'Road',
           'Rd.'  : 'Road',
           'St'   : 'Street',
           'street' :"Street",
           'Ct'   : "Court",
           'Cir'  : "Circle",
           'Cr'   : "Court",
           'ave'  : 'Avenue',
           'Hwg'  : 'Highway',
           'Hwy'  : 'Highway',
           'St.'  : 'Street',
           'Sq'   : "Square",
           '420'  : "420",
           'Ext'  : "Extension",
        }


# In[144]:

#updating street names to correct form
def update_name(name, mapping, regex):                         
    m = regex.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping:
            name = re.sub(regex, mapping[street_type], name)     #replacing abbreviation with mapped value

    return name

for street_type, ways in st_types.iteritems():       #iterating through all the street names and fixing it
    for name in ways:
        better_name = update_name(name, mapping, street_type_re)
        print name, "=>", better_name


# >All abbreviations in street names are fixed by mapping.

# ### Problems in zip codes

# In[145]:

# Auditing all zip codes in the given data
from collections import defaultdict     

def audit_zipcode(invalid_zipcodes, zipcode):
    twoDigits = zipcode[0:2]        #validating zip code and adding it to invalid if not satisfying the conditions
    
    if not zipcode.isdigit():
        invalid_zipcodes[twoDigits].add(zipcode)
    
    elif twoDigits !="96" :
        invalid_zipcodes[twoDigits].add(zipcode) 
    elif len(zipcode)>5:
        invalid_zipcodes[twoDigits].add(zipcode) 
        
def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")  

def audit_zip(osmfile):
    osm_file = open(osmfile, "r")
    invalid_zipcodes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)): #calling audit_zipcode iterating on all the zipcodes

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zipcode(tag):
                    audit_zipcode(invalid_zipcodes,tag.attrib['v'])

    return invalid_zipcodes

map_zipcode = audit_zip(map_data)
map_zipcode


# >Some zip codes contain hypen b/w them.
# 
# >One type of zip code contain text.

# In[146]:

def update_zip(zipcode):                          # Fixing zip codes in case it don't match the desired pattern.
    testNum = re.findall('[a-zA-Z]*', zipcode)
    if testNum:
        testNum = testNum[0]
    testNum.strip('-')
    if testNum == "HI":
        convertedZipcode = (re.findall(r'\d+', zipcode))
        if convertedZipcode:
            if convertedZipcode.__len__() == 2:
                return (re.findall(r'\d+', zipcode))[0] + "-" +(re.findall(r'\d+', zipcode))[1]
            else:
                return (re.findall(r'\d+', zipcode))[0]
    else:        
        return (re.findall(r'\d+', zipcode))[0]
for street_type, ways in map_zipcode.iteritems():
    for name in ways:
        better_name = update_zip(name)
        print name, "=>", better_name


# >Zip code errors were solved i.e removing hypen and text characters.

# ## Formatting data in required json Format

# In[147]:

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]    #created field for json object
# function that corrects incorrect street names
def update_name(name, mapping):    
    for key in mapping:
        if key in name:
            name = string.replace(name,key,mapping[key])
    return name

def shape_element(element):  #shaping osm data in json format
    node = {}
    node["created"]={}
    node["address"]={}
    node["pos"]=[]
    refs=[]
    
    # we only process the node and way tags
    if element.tag == "node" or element.tag == "way" :
        if "id" in element.attrib:
            node["id"]=element.attrib["id"]
        node["type"]=element.tag

        if "visible" in element.attrib.keys():
            node["visible"]=element.attrib["visible"]
      
        # the key-value pairs with attributes in the CREATED list are added under key "created"
        for elem in CREATED:
            if elem in element.attrib:
                node["created"][elem]=element.attrib[elem]
                
        # attributes for latitude and longitude are added to a "pos" array
        # include latitude value        
        if "lat" in element.attrib:
            node["pos"].append(float(element.attrib["lat"]))
        # include longitude value    
        if "lon" in element.attrib:
            node["pos"].append(float(element.attrib["lon"]))

        #iterating over tags in the given data.
        for tag in element.iter("tag"):
            if not(problemchars.search(tag.attrib['k'])):
                if tag.attrib['k'] == "addr:housenumber":
                    node["address"]["housenumber"]=tag.attrib['v']
                # updating zip codes by calling update_zip method defined above    
                if tag.attrib['k'] == "addr:postcode":
                    node["address"]["postcode"]=tag.attrib['v']
                    node["address"]["postcode"]=update_zip(node["address"]["postcode"])
                
                # handling the street attribute, update incorrect names using the strategy developed before   
                if tag.attrib['k'] == "addr:street":
                    node["address"]["street"]=tag.attrib['v']
                    node["address"]["street"] = update_name(node["address"]["street"], mapping)

                if tag.attrib['k'].find("addr")==-1:
                    node[tag.attrib['k']]=tag.attrib['v']
                    
        for nd in element.iter("nd"):
             refs.append(nd.attrib["ref"])
                
        if node["address"] =={}:
            node.pop("address", None)

        if refs != []:
           node["node_refs"]=refs
            
        return node
    else:
        return None

# process the xml openstreetmap file, write a json out file and return a list of dictionaries
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


# In[148]:

# process the file
data = process_map(map_data, True)


# In[149]:

#Above method shapes the data in following JSON Format
data[352]


# ## Storing processed json data to MongoDB

# In[150]:

client = MongoClient()      # making mongodb connection importing json data to mongo db locally
db = client.honolulu
collection = db.honolulu
#collection.insert(data)       #insertion is done one time only ucomment it if haven't inserted.


# In[151]:

collection         #collection named honolulu for this data


# ## Data Overview with MongoDB

# In[152]:

os.path.getsize(map_data)/1024/1024        #Size of xml file in MB


# In[153]:

os.path.getsize("honolulu_hawaii.osm.json")/1024/1024      #Size Of json file in MB


# In[154]:

collection.find().count()      #Total number of documents inside Mongo DB collection honolulu


# In[155]:

# Number of unique users
len(collection.group(["created.uid"], {}, {"count":0}, "function(o, p){p.count++}"))


# In[156]:

# Number of nodes
collection.find({"type":"node"}).count()


# In[157]:

# Number of ways
collection.find({"type":"way"}).count()


# In[158]:

#Top five users with most contributions
pipeline = [{"$group":{"_id": "$created.user",     
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}]
result = collection.aggregate(pipeline)
x=list(result)
x


# this shows that Tom_Holland is most active user.

# In[159]:

#Proportion of the top user contributions
top_user_prop = [{"$group":{"_id": "$created.user",
                       "count": {"$sum": 1}}},
            {"$project": {"proportion": {"$divide" :["$count",collection.find().count()]}}},
            {"$sort": {"proportion": -1}},
            {"$limit": 5}]
result = list(collection.aggregate(top_user_prop))
result


# 38% contribution was alone by Tom_Holland and others have very less compared to him.

# ## Additional Ideas and further exploration

# In[160]:

#Most common amenities in the area
aminity=[{"$match":{"amenity":{"$exists":1}}},
                              {"$group":{"_id":"$amenity","count":{"$sum":1}}},
                              {"$sort":{"count":-1}},{"$limit":10}]
result=list(collection.aggregate(aminity))
result


# Most frequent amenities are parking, restaurant, fast_food respectively.

# In[161]:

# Types of parking and their frequency 
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"parking", "parking":{"$exists":1}}}, 
            {"$group":{"_id":"$parking", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result


# Surface Parking is mostly performed so good road parking facilities in the area

# In[162]:

#cuisines in restaurants
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant", "cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result


# In restaurant most popular cuisine is Pizzas.

# In[163]:

#cuisines in fast_food
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"fast_food", "cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result


# burger is most popular cuisine in fast_food

# In[164]:

#Overall cusines of Honolulu
pipeline = [{"$match":{"cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result


# This data shows that most people prefer having Burgers in cuisines

# In[165]:

#different type of buildings in Honolulu dataset
pipeline = [{"$match":{"building":{"$exists":1}}}, 
            {"$group":{"_id":"$building", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result


# There are huge no of buildings in dataset 
# 
# Most of the building type were unspecified i.e 3427
# 
# Although most common buildings are apartments, houses and commercial

# In[166]:

#Different types of shops in Honolulu
pipeline = [{"$match":{"shop":{"$exists":1}}}, 
            {"$group":{"_id":"$shop", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result


# So large no. of supermarkets, convenience and clothes stores are there in Honolulu

# In[167]:

#name of different schools
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity": "school", "name":{"$exists":1}}},
            {"$group":{"_id":"$name", "count":{"$sum":1}}},
            {"$sort":{"count":-1}},{"$limit":10}]
result = list(collection.aggregate(pipeline))
result


# There are only single branch of every school in this city.

# In[168]:

# types of roads or highways
pipeline = [{'$match': {'highway': { '$exists': 1}}}, 
        {'$group': {'_id': '$highway',
                    'count': {'$sum': 1}}}, 
        {'$sort': {'count': -1}},
        {'$limit': 5}]
result=list(collection.aggregate(pipeline)) 
result


# So mostly residential area is there in the city which highway covers

# In[169]:

# types of religion followed
pipeline = [{"$match":{"religion":{"$exists":1}}},
                      {"$group":{"_id":"$religion", "count":{"$sum":1}}},
                      {"$sort":{"count":-1}}]
result=list(collection.aggregate(pipeline)) 
result


# So mostly Christian religion is followed ...
# 
# ### Additional Idea
# 
# For improving the database some validations should be applied while filling the information in specific way like some format or user interface should be provided to enter the data with inbuilt valdiations and warnings.
# 
# And also user who contributed most should be displayed on the website so that others also try to contribute more by getting motivation from his/her work.
# 
# >From above two ideas firstly data is entered in more proper format.
# Secondly contribution increases if you give some credit to persons who contributed more.

# # Conclusion

# From Data Wrangling on Honolulu, Hawai, USA openstreet data of size greater than 50 MB I found that:
# 
# 464 people were involved in its map editing out of which 1 contributed the most around 38%.
# 
# Some errors in street name abbreviations and zip codes were found while auditing the dataset which were fixed by mapping.
# 
# Parking is most frequent amenity in the area and in parking surface parking is most common.
# 
# People there are fond of pizzas and burgers and other fast food items and drinking coffee is also very common practice.
# 
# There are many supermarkets, clothing shopping stores and big buildings in the city.
# 
# Mostly Christians are there in that area.
# 
# So data must have lots of other hidden information as any type of tag is allowed and could be more further explored.

# ## Refrences

# https://docs.google.com/document/d/1F0Vs14oNEs2idFJR3C_OPxwS6L0HPliOii-QpbmrMo4/pub#h.ueey7dly83g7
# 
# https://mapzen.com/data/metro-extracts/metro/honolulu_hawaii/
# 
# Case study of lectures
# 
# http://wiki.openstreetmap.org/wiki/

# In[ ]:



