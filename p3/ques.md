
# Data Wrangling with MongoDB

### OpenStreetMap Sample Project

#### Map Area: Honolulu, Hawaii, United States

http://www.openstreetmap.org/#map=10/21.4860/-157.9710




```python
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
```


```python
#Fetching osm data in python variable map_data
datadir = ""
datafile = "honolulu_hawaii.osm"
map_data = os.path.join(datadir, datafile)
```

##  Problems Encountered in the Map(Auditing)

#### Description of Map tags
{'bounds': 1,
 'member': 1612,
 'nd': 288004,
 'node': 242190,
 'osm': 1,
 'relation': 384,
 'tag': 117607,
 'way': 25500}
Here we founded that there are 242190 nodes, 117607 tags, 25500 ways and 384 relation.


```python
#people invovlved in the map editing.
def process_map(filename):           
    users = set()
    for _, element in ET.iterparse(filename):        ##iterating through unique userid to find number of users involved
        for e in element:
            if 'uid' in e.attrib:
                users.add(e.attrib['uid'])
    return users
users = process_map(map_data)
len(users)
```




    464




```python
lower = re.compile(r'^([a-z]|_)*$')                    # Regular Expressions for different cases matching
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
```

>These expressions are used for validating a string in particular format. 


```python
# initial expected street names
expected = ["Street", "Avenue", "Boulevard","Broadway","Drive", "Court", "Place", "Square", "Lane",
            "Road", "Trail", "Parkway"]
```

>Initially we consider some common words as expected street names.

### Auditing Problems associating with street name abbreviations
{'106': set(['Pualei Cir, Apt 106']),
 'Ave': set(['Kalakaua Ave']),
 'Blvd': set(['Ala Moana Blvd']),
 'Center': set(['Enchanted Lakes Shopping Center']),
 'Circle': set(['Delay Circle', 'Papu Circle', 'Pualei Circle']),
 'Dr': set(['Kipapa Dr']),
 'Highway': set(['Farrington Highway',
                 "Kalaniana'ole Highway",
                 'Kalanianaole Highway',
                 u'Kalaniana\u2019ole Highway',
                 'Kamehameha Highway',
                 'Nimitz Highway',
                 'Pali Highway']),
 'Honolulu': set(['Moanalua, Honolulu']),
 'Hwy': set(['Kamehameha Hwy']),
 'Ike': set(['Ala Ike']),
 'Kailua,': set(['Kaelepulu Dr, Kailua,']),
 'King': set(['South King']),
 'Loop': set(['98-402 Koauka Loop',
              '98-410 Koauka Loop',
              '98-500 Koauka Loop',
              '98-501 Koauka Loop']),
 'Mall': set(['Fort Street Mall', 'McCarthy Mall']),
 'Momi': set(['Pali Momi']),
 'Pkwy': set(['Meheula Pkwy']),
 'St': set(['Ala Pumalu St', 'Lusitania St']),
 'St.': set(['Lusitania St.']),
 'Terrace': set(['Round Top Terrace']),
 'Walk': set(['Beach Walk']),
 'Way': set(['Ainakea Way',
             'Coelho Way',
             'Kuaaina Way',
             'Pualani Way',
             'Wai Nani Way']),
 'highway': set(['kanehameha highway']),
 'king': set(['king'])}
>We found that lot of abbreviations are used in the street names.

>So some fix of names is required for that which can be done by mapping abbreviations to their full form.


```python
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
```


```python
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

```

    Ala Ike => Ala Ike
    Lusitania St. => Lusitania Street
    Pualani Way => Pualani Way
    Wai Nani Way => Wai Nani Way
    Kuaaina Way => Kuaaina Way
    Ainakea Way => Ainakea Way
    Coelho Way => Coelho Way
    Papu Circle => Papu Circle
    Pualei Circle => Pualei Circle
    Delay Circle => Delay Circle
    Pali Highway => Pali Highway
    Farrington Highway => Farrington Highway
    Kamehameha Highway => Kamehameha Highway
    Kalaniana’ole Highway => Kalaniana’ole Highway
    Kalanianaole Highway => Kalanianaole Highway
    Kalaniana'ole Highway => Kalaniana'ole Highway
    Nimitz Highway => Nimitz Highway
    Pali Momi => Pali Momi
    Moanalua, Honolulu => Moanalua, Honolulu
    Kamehameha Hwy => Kamehameha Highway
    Kaelepulu Dr, Kailua, => Kaelepulu Dr, Kailua,
    Kipapa Dr => Kipapa Drive
    kanehameha highway => kanehameha highway
    South King => South King
    Enchanted Lakes Shopping Center => Enchanted Lakes Shopping Center
    Meheula Pkwy => Meheula Parkway
    Fort Street Mall => Fort Street Mall
    McCarthy Mall => McCarthy Mall
    Ala Pumalu St => Ala Pumalu Street
    Lusitania St => Lusitania Street
    Pualei Cir, Apt 106 => Pualei Cir, Apt 106
    98-501 Koauka Loop => 98-501 Koauka Loop
    98-500 Koauka Loop => 98-500 Koauka Loop
    98-402 Koauka Loop => 98-402 Koauka Loop
    98-410 Koauka Loop => 98-410 Koauka Loop
    king => king
    Beach Walk => Beach Walk
    Round Top Terrace => Round Top Terrace
    Ala Moana Blvd => Ala Moana Boulevard
    Kalakaua Ave => Kalakaua Avenue


>All abbreviations in street names are fixed by mapping.

### Problems in zip codes
defaultdict(set,                                     # These all zipcodes are not in proper format
            {'96': {'96712-9998',
              '96734-9998',
              '96815-2518',
              '96815-2830',
              '96815-2834',
              '96817-1713',
              '96825-9998',
              '96826-4427'},
             'HI': {'HI 96819'}})
>Some zip codes contain hypen b/w them.

>One type of zip code contain text.
def update_zip(zipcode):                          # Fixing zip codes in case it don't match the desired pattern.
    return (re.findall(r'\d{5}', zipcode))[0]
for street_type, ways in map_zipcode.iteritems():
    for name in ways:
        better_name = update_zip(name)
        print name, "=>", better_nameHI 96819 => 96819
96815-2518 => 96815
96734-9998 => 96734
96826-4427 => 96826
96817-1713 => 96817
96815-2830 => 96815
96815-2834 => 96815
96712-9998 => 96712
96825-9998 => 96825

>Zip code errors were solved i.e removing hypen and text characters.

## Formatting data in required json Format
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]    #created field for json object
# Here data is processed into above fields types in Json format.# process the file
data = process_map(map_data, True)#Above method shapes the data in following JSON Format
data[352]

{'created': {'changeset': '3561802',
  'timestamp': '2010-01-07T13:30:40Z',
  'uid': '147510',
  'user': 'woodpeck_fixbot',
  'version': '2'},
 'id': '110502291',
 'pos': [21.385667, -158.102447],
 'type': 'node'}
## Storing processed json data to MongoDB


```python
client = MongoClient()      # making mongodb connection importing json data to mongo db locally
db = client.honolulu
collection = db.honolulu
#collection.insert(data)       #insertion is done one time only ucomment it if haven't inserted.
```


```python
collection         #collection named honolulu for this data
```




    Collection(Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), u'honolulu'), u'honolulu')



## Data Overview with MongoDB


```python
os.path.getsize(map_data)/1024/1024        #Size of xml file in MB
```




    50




```python
os.path.getsize("honolulu_hawaii.osm.json")/1024/1024      #Size Of json file in MB
```




    72




```python
collection.find().count()      #Total number of documents inside Mongo DB collection honolulu
```




    267690




```python
# Number of unique users
len(collection.group(["created.uid"], {}, {"count":0}, "function(o, p){p.count++}"))

```




    461




```python
# Number of nodes
collection.find({"type":"node"}).count()
```




    242159




```python
# Number of ways
collection.find({"type":"way"}).count()
```




    25495




```python
#Top five users with most contributions
pipeline = [{"$group":{"_id": "$created.user",     
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}]
result = collection.aggregate(pipeline)
x=list(result)
x

```




    [{u'_id': u'Tom_Holland', u'count': 102211},
     {u'_id': u'cbbaze', u'count': 14995},
     {u'_id': u'ikiya', u'count': 12807},
     {u'_id': u'kr4z33', u'count': 9470},
     {u'_id': u'Chris Lawrence', u'count': 9214}]



this shows that Tom_Holland is most active user.


```python
#Proportion of the top user contributions
top_user_prop = [{"$group":{"_id": "$created.user",
                       "count": {"$sum": 1}}},
            {"$project": {"proportion": {"$divide" :["$count",collection.find().count()]}}},
            {"$sort": {"proportion": -1}},
            {"$limit": 5}]
result = list(collection.aggregate(top_user_prop))
result
```




    [{u'_id': u'Tom_Holland', u'proportion': 0.3818259927528111},
     {u'_id': u'cbbaze', u'proportion': 0.05601628749673129},
     {u'_id': u'ikiya', u'proportion': 0.04784265381598117},
     {u'_id': u'kr4z33', u'proportion': 0.03537674175352087},
     {u'_id': u'Chris Lawrence', u'proportion': 0.03442041167021555}]



38% contribution was alone by Tom_Holland and others have very less compared to him.

## Additional Ideas and further exploration


```python
#Most common amenities in the area
aminity=[{"$match":{"amenity":{"$exists":1}}},
                              {"$group":{"_id":"$amenity","count":{"$sum":1}}},
                              {"$sort":{"count":-1}},{"$limit":10}]
result=list(collection.aggregate(aminity))
result
```




    [{u'_id': u'parking', u'count': 391},
     {u'_id': u'restaurant', u'count': 218},
     {u'_id': u'fast_food', u'count': 112},
     {u'_id': u'school', u'count': 85},
     {u'_id': u'toilets', u'count': 75},
     {u'_id': u'cafe', u'count': 64},
     {u'_id': u'place_of_worship', u'count': 38},
     {u'_id': u'library', u'count': 38},
     {u'_id': u'fire_station', u'count': 36},
     {u'_id': u'college', u'count': 29}]



Most frequent amenities are parking, restaurant, fast_food respectively.


```python
# Types of parking and their frequency 
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"parking", "parking":{"$exists":1}}}, 
            {"$group":{"_id":"$parking", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result
```




    [{u'_id': u'surface', u'count': 135},
     {u'_id': u'multi-storey', u'count': 54},
     {u'_id': u'underground', u'count': 3}]



Surface Parking is mostly performed so good road parking facilities in the area


```python
#cuisines in restaurants
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant", "cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result
```




    [{u'_id': u'pizza', u'count': 8},
     {u'_id': u'japanese', u'count': 7},
     {u'_id': u'regional', u'count': 6},
     {u'_id': u'chinese', u'count': 5},
     {u'_id': u'american', u'count': 5},
     {u'_id': u'international', u'count': 4},
     {u'_id': u'thai', u'count': 4},
     {u'_id': u'italian', u'count': 3},
     {u'_id': u'asian', u'count': 3},
     {u'_id': u'indian', u'count': 2}]



In restaurant most popular cuisine is Pizzas.


```python
#cuisines in fast_food
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"fast_food", "cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result
```




    [{u'_id': u'burger', u'count': 18},
     {u'_id': u'sandwich', u'count': 5},
     {u'_id': u'mexican', u'count': 4},
     {u'_id': u'pizza', u'count': 3},
     {u'_id': u'sushi', u'count': 3},
     {u'_id': u'ice_cream', u'count': 1},
     {u'_id': u'asian', u'count': 1},
     {u'_id': u'american', u'count': 1},
     {u'_id': u'hawaiian', u'count': 1},
     {u'_id': u'regional', u'count': 1}]



burger is most popular cuisine in fast_food


```python
#Overall cusines of Honolulu
pipeline = [{"$match":{"cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result
```




    [{u'_id': u'burger', u'count': 22},
     {u'_id': u'coffee_shop', u'count': 12},
     {u'_id': u'pizza', u'count': 11},
     {u'_id': u'japanese', u'count': 8},
     {u'_id': u'regional', u'count': 7},
     {u'_id': u'american', u'count': 7},
     {u'_id': u'mexican', u'count': 6},
     {u'_id': u'chinese', u'count': 6},
     {u'_id': u'sandwich', u'count': 6},
     {u'_id': u'sushi', u'count': 5}]



This data shows that most people prefer having Burgers in cuisines


```python
#different type of buildings in Honolulu dataset
pipeline = [{"$match":{"building":{"$exists":1}}}, 
            {"$group":{"_id":"$building", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result
```




    [{u'_id': u'yes', u'count': 3427},
     {u'_id': u'apartments', u'count': 375},
     {u'_id': u'house', u'count': 363},
     {u'_id': u'commercial', u'count': 266},
     {u'_id': u'school', u'count': 137},
     {u'_id': u'hangar', u'count': 48},
     {u'_id': u'hotel', u'count': 44},
     {u'_id': u'roof', u'count': 40},
     {u'_id': u'retail', u'count': 28},
     {u'_id': u'college', u'count': 27}]



There are huge no of buildings in dataset 

Most of the building type were unspecified i.e 3427

Although most common buildings are apartments, houses and commercial


```python
#Different types of shops in Honolulu
pipeline = [{"$match":{"shop":{"$exists":1}}}, 
            {"$group":{"_id":"$shop", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pipeline))
result
```




    [{u'_id': u'supermarket', u'count': 73},
     {u'_id': u'convenience', u'count': 42},
     {u'_id': u'clothes', u'count': 34},
     {u'_id': u'department_store', u'count': 13},
     {u'_id': u'gift', u'count': 11},
     {u'_id': u'bakery', u'count': 7},
     {u'_id': u'mall', u'count': 7},
     {u'_id': u'doityourself', u'count': 6},
     {u'_id': u'hairdresser', u'count': 5},
     {u'_id': u'jewelry', u'count': 5}]



So large no. of supermarkets, convenience and clothes stores are there in Honolulu


```python
#name of different schools
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity": "school", "name":{"$exists":1}}},
            {"$group":{"_id":"$name", "count":{"$sum":1}}},
            {"$sort":{"count":-1}},{"$limit":10}]
result = list(collection.aggregate(pipeline))
result

```




    [{u'_id': u"Kawaiaha'o Church School", u'count': 1},
     {u'_id': u'The Kamehameha Schools', u'count': 1},
     {u'_id': u'Noelani School', u'count': 1},
     {u'_id': u"Ka'elepulu Elementary", u'count': 1},
     {u'_id': u'Hawaii School for the Deaf and the Blind', u'count': 1},
     {u'_id': u'Mililani Ike Elementary School', u'count': 1},
     {u'_id': u'R. L. Stevenson Middle School', u'count': 1},
     {u'_id': u'Shade House', u'count': 1},
     {u'_id': u'Highlands Intermediate School', u'count': 1},
     {u'_id': u'Mid-Pacific Institute', u'count': 1}]



There are only single branch of every school in this city.


```python
# types of roads or highways
pipeline = [{'$match': {'highway': { '$exists': 1}}}, 
        {'$group': {'_id': '$highway',
                    'count': {'$sum': 1}}}, 
        {'$sort': {'count': -1}},
        {'$limit': 5}]
result=list(collection.aggregate(pipeline)) 
result
```




    [{u'_id': u'residential', u'count': 6832},
     {u'_id': u'service', u'count': 4538},
     {u'_id': u'living_street', u'count': 1759},
     {u'_id': u'turning_circle', u'count': 1354},
     {u'_id': u'footway', u'count': 555}]



So mostly residential area is there in the city which highway covers


```python
# types of religion followed
pipeline = [{"$match":{"religion":{"$exists":1}}},
                      {"$group":{"_id":"$religion", "count":{"$sum":1}}},
                      {"$sort":{"count":-1}}]
result=list(collection.aggregate(pipeline)) 
result
```




    [{u'_id': u'christian', u'count': 25},
     {u'_id': u'buddhist', u'count': 7},
     {u'_id': u'muslim', u'count': 1}]



So mostly Christian religion is followed ...

### Additional Idea

For improving the database some validations should be applied while filling the information in specific way like some format or user interface should be provided to enter the data with inbuilt valdiations and warnings.
This interface will consist of all general formats information like pincode should be of 5 digits all numeric.
But validation also depends on location like in India pincode is of 6 digits therefore some changes are also necessary based on location.

And also user who contributed most should be displayed on the website so that others also try to contribute more by getting motivation from his/her work.
If there will be competitive environment then everyone will try their best in terms of quantity as well as quality of the data.

>From above two ideas firstly data is entered in more proper format.

>Secondly contribution and quality increases if you give some credit to persons who contributed more.

# Conclusion

From Data Wrangling on Honolulu, Hawai, USA openstreet data of size greater than 50 MB I found that:

464 people were involved in its map editing out of which 1 contributed the most around 38%.

Some errors in street name abbreviations and zip codes were found while auditing the dataset which were fixed by mapping.

Parking is most frequent amenity in the area and in parking surface parking is most common.

People there are fond of pizzas and burgers and other fast food items and drinking coffee is also very common practice.

There are many supermarkets, clothing shopping stores and big buildings in the city.

Mostly Christians are there in that area.

So data must have lots of other hidden information as any type of tag is allowed and could be more further explored.

## Refrences

https://docs.google.com/document/d/1F0Vs14oNEs2idFJR3C_OPxwS6L0HPliOii-QpbmrMo4/pub#h.ueey7dly83g7

https://mapzen.com/data/metro-extracts/metro/honolulu_hawaii/

Case study of lectures

http://wiki.openstreetmap.org/wiki/


```python

```
