import ujson
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Pre-processing data before indexing
with open('crawler_results.json', 'r') as doc:
    scraper_results = doc.read()

pubName = []
pubURL = []
pubCUAuthor = []
pubDate = []
pubAuthorUrl=[]
data_dict = ujson.loads(scraper_results)
array_length = len(data_dict)
print("found ", array_length, " data")

# Separate name, url, date, author in different file
for item in data_dict:
    pubName.append(item["name"])
    pubURL.append(item["pub_url"])
    pubCUAuthor.append(item["cu_author"])
    pubDate.append(item["date"])
    pubAuthorUrl.append(item["author_url"])
with open('pub_name.json', 'w') as f:
    ujson.dump(pubName, f)
with open('pub_url.json', 'w') as f:
    ujson.dump(pubURL, f)
with open('author.json', 'w') as f:
    ujson.dump(pubCUAuthor, f)
with open('pub_date.json', 'w') as f:
    ujson.dump(pubDate, f)
with open('pub_authorurl.json', 'w') as f:
    ujson.dump(pubAuthorUrl, f)


# Open a file with publication names in read mode
with open('pub_name.json', 'r') as f:
    publication = f.read()

# Load JSON File
pubName = ujson.loads(publication)

# Predefined stopwords in nltk are used
stop_words = stopwords.words('english')
p_stemmer = PorterStemmer()
pub_list_stemmed = []
pub_list = []
pub_list_nsp = []
print("found ", len(pubName), " publication specimen")

for pub in pubName:
    # Splitting strings to tokens(words)
    words = word_tokenize(pub)
    stem_word = ""
    for w in words:
        if w.lower() not in stop_words:
            stem_word += p_stemmer.stem(w) + " "
    pub_list_stemmed.append(stem_word)
    pub_list.append(pub)

# Removing all below characters
special_characters = '''!()-—[]{};:'"\, <>./?@#$%^&*_~0123456789+=’‘'''
for pub in pub_list:
    no_sp_pub = ""
    if len(pub.split()) == 1:
        pub_list_nsp.append(pub)
    else:
        for p in pub:
            if p in special_characters:
                no_sp_pub += ' '
            else:
                no_sp_pub += p
        pub_list_nsp.append(no_sp_pub)

# Stemming Process
pub_list_stemmed_nsp = []
for name in pub_list_nsp:
    words = word_tokenize(name)
    stem_word = ""
    for word in words:
        if word.lower() not in stop_words:
            stem_word += p_stemmer.stem(word) + ' '
    pub_list_stemmed_nsp.append(stem_word.lower())

pub_dict = {}

# Indexing process
for i in range(len(pub_list_stemmed_nsp)):
    for j in pub_list_stemmed_nsp[i].split():
        if j not in pub_dict:
            pub_dict[j] = [i]
        else:
            pub_dict[j].append(i)

print(len(pub_list_nsp))
print(len(pub_list_stemmed_nsp))
print(len(pub_list_stemmed))
print(len(pub_list))

with open('pub_list_stemmed.json', 'w') as f:
    ujson.dump(pub_list_stemmed, f)

with open('pub_dict_indexed.json', 'w') as f:
    ujson.dump(pub_dict, f)

# Open a file with publication names in read mode
with open('author.json', 'r') as f:
    authors = f.read()

# Load JSON File
pubCUAuthor = ujson.loads(authors)

# Predefined stopwords in nltk are used
auth_list_stemmed = []
auth_list = []
auth_list_nsp = []
print("found ", len(pubCUAuthor), " author specimen")

for auth in pubCUAuthor:
    # Splitting strings to tokens(words)
    words = word_tokenize(auth)
    stem_word = ""
    for w in words:
        if w.lower() not in stop_words:
            stem_word += p_stemmer.stem(w) + " "
    auth_list_stemmed.append(stem_word)
    auth_list.append(auth)

# Removing all below characters
for auth in auth_list:
    no_sp_auth = ""
    if len(auth.split()) == 1:
        auth_list_nsp.append(auth)
    else:
        for a in auth:
            if a in special_characters:
                no_sp_auth += ' '
            else:
                no_sp_auth += a
        auth_list_nsp.append(no_sp_auth)

# Stemming Process
auth_list_nsp_stemmed = []
for name in auth_list_nsp:
    words = word_tokenize(name)
    stem_word = ""
    for a in words:
        if a.lower() not in stop_words:
            stem_word += p_stemmer.stem(a) + ' '
    auth_list_nsp_stemmed.append(stem_word.lower())

auth_dict = {}

# Indexing process
for i in range(len(auth_list_nsp_stemmed)):
    for j in auth_list_nsp_stemmed[i].split():
        if j not in auth_dict:
            auth_dict[j] = [i]
        else:
            auth_dict[j].append(i)

print(len(auth_list_nsp))
print(len(auth_list_nsp_stemmed))
print(len(auth_list_stemmed))
print(len(auth_list))

with open('auth_list_stemmed.json', 'w') as f:
    ujson.dump(auth_list_stemmed, f)

with open('auth_dict_indexed.json', 'w') as f:
    ujson.dump(auth_dict, f)