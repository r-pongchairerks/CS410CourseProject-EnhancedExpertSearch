from flask import Flask, redirect, url_for
from flask import render_template, request, jsonify
import wikipedia
import json
import os
import metapy
import requests
import base64
import sys
import re



app = Flask(__name__) 
environ = 'development'
dataconfig = json.loads(open("config.json", "r").read())
app.dataenv = dataconfig[environ]
app.rootpath = dataconfig[environ]["rootpath"]
app.datasetpath = dataconfig[environ]['datasetpath']
app.searchconfig = dataconfig[environ]['searchconfig']
index = metapy.index.make_inverted_index(app.searchconfig)
query = metapy.index.Document()
uni_list = json.loads(open(dataconfig[environ]["unispath"],'r').read())["unis"]
loc_list = json.loads(open(dataconfig[environ]["locspath"],'r').read())["locs"]

@app.route('/')
def home():
    return render_template('index.html',uni_list= uni_list,loc_list=loc_list)

@app.route('/admin')
def admin():
    return render_template('admin.html')

def filtered_results(results,num_results,min_score,selected_uni_filters,selected_loc_filters):
    filtered_results = []
    universities = []
    states =[]
    countries = []
    res_cnt = 0
    # print (selected_uni_filters,selected_loc_filters)
    for res in results:
        university = index.metadata(res[0]).get('university')
        state = index.metadata(res[0]).get('state')
        country = index.metadata(res[0]).get('country') 
        if (res[1]>min_score) and (state in selected_loc_filters or country in selected_loc_filters) and (university in selected_uni_filters) :
            filtered_results.append(res)
            res_cnt += 1
            universities.append(university)
            states.append(state)
            countries.append(country)
            if res_cnt == num_results:
                break
    return filtered_results,universities,states,countries

@app.route('/search', methods=['POST'])
def search():
    data = json.loads(request.data)
    querytext = data['query']
    num_results = data['num_results']
    selected_loc_filters = data['selected_loc_filters']
    selected_uni_filters = data['selected_uni_filters']

    query = metapy.index.Document()
    query.content(querytext)
    min_score = 0.01

    # Dynamically load the ranker
    sys.path.append(app.rootpath + "/expertsearch")

    from ranker import load_ranker

    ranker = load_ranker(app.searchconfig)

    results = ranker.score(index, query, 100) 

    results,universities,states,countries = filtered_results(results,num_results,min_score,selected_uni_filters,selected_loc_filters)

    doc_names = [index.metadata(res[0]).get('doc_name') for res in results]
    depts = [index.metadata(res[0]).get('department') for res in results]
    fac_names = [index.metadata(res[0]).get('fac_name') for res in results]
    fac_urls = [index.metadata(res[0]).get('fac_url') for res in results]

    previews = _get_doc_previews(doc_names,querytext)
    emails = [index.metadata(res[0]).get('email') for res in results]


    docs = list(zip(doc_names, previews, emails,universities,depts,fac_names,fac_urls,states,countries))

    return jsonify({
        "docs": docs
    })

@app.route("/admin/ranker/get")
def get_ranker():
    ranker_path = app.rootpath + "/expertsearch/ranker.py"
    ranker_contents = open(ranker_path, 'r').read()

    return jsonify({
        "ranker_contents": ranker_contents
    })

@app.route("/admin/ranker/set", methods=["POST"])
def set_ranker():
    data = json.loads(request.data)

    projectId = data["projectId"]
    apiToken = data["apiToken"]

    ranker_url = "https://lab.textdata.org/api/v4/projects/" + projectId + "/repository/files/search_eval.py?ref=master&private_token=" + apiToken
    resp = requests.get(ranker_url)

    gitlab_resp = json.loads(resp.content)
    file_content = gitlab_resp["content"]
    ranker_path = app.rootpath + "/expertsearch/ranker.py"

    with open(ranker_path, 'wb') as f:
        f.write(base64.b64decode(file_content))
        f.close()

    return "200"

def wiki_search(query):
    try:
        return wikipedia.summary(query)
    except Exception:
        for new_query in wikipedia.search(query):
            try:
                return wikipedia.summary(new_query)
            except Exception:
                pass
    return "I don't know about "+query

# sample test data
# faculties = []
# faculty1 = {
#     "url": "http://university.edu/faculty/john_doe",
#     "name": "John Doe",
#     "research_areas": ["Machine Learning", "Artificial Intelligence"],
#     "research_interests": "Deep learning, neural networks, and AI ethics",
#     "education": "Ph.D. in Computer Science from MIT"
# }
# faculty2 = {
#     "url": "http://university.edu/faculty/jane_smith",
#     "name": "Jane Smith",
#     "research_areas": ["Quantum Computing", "Cryptography", "Machine Learning"],
#     "research_interests": "Quantum algorithms and security protocols",
#     "education": "Ph.D. in Physics from Harvard"
# }
# faculties.append(faculty1)
# faculties.append(faculty2)

# def get_info_from_name(query):
#     for faculty in faculties:
#         if faculty["name"].lower() == query.lower():
#             faculty_info = (
#                 "Name: {}\n"
#                 "URL: {}\n"
#                 "Research Areas: {}\n"
#                 "Research Interests: {}\n"
#                 "Education: {}".format(
#                     faculty['name'],
#                     faculty['url'],
#                     ', '.join(faculty['research_areas']),
#                     faculty['research_interests'],
#                     faculty['education']
#                 )
#             )
#             return faculty_info
#     return "No faculty member found with the name: {}".format(query)

# def get_names_research_areas(query):
#     matching_faculties = []

#     for faculty in faculties:
#         if any(query.lower() == area.lower() for area in faculty["research_areas"]):
#             faculty_info = (
#                 "Name: {}\n"
#                 "URL: {}\n"
#                 "Research Areas: {}\n"
#                 "Research Interests: {}\n"
#                 "Education: {}\n\n".format(
#                     faculty['name'],
#                     faculty['url'],
#                     ', '.join(faculty['research_areas']),
#                     faculty['research_interests'],
#                     faculty['education']
#                 )
#             )
#             matching_faculties.append(faculty_info)

#     if matching_faculties:
#         return ''.join(matching_faculties)
#     else:
#         return "No faculty member found whose research area is in: {}".format(query)


# @app.route("/chat", methods=["GET"])
# def search_expert_from_query(query):
#     # Regex patterns for different types of queries
#     name_search_pattern = re.compile(r"^search name: (.+)")
#     area_search_pattern = re.compile(r"^search area: (.+)")
    
#     name_match = name_search_pattern.match(query)
#     if name_match:
#         faculty_name = name_match.group(1).strip()
#         return get_info_from_name(faculty_name)
    
#     area_match = area_search_pattern.match(query)
#     if area_match:
#         research_area = area_match.group(1).strip()
#         return get_names_research_areas(research_area)
    
#     return "Invalid search query"

@app.route("/chat", methods=["POST"])
def get_chat_response():
    data = json.loads(request.data.decode('utf-8'))
    query = data["query"].lower()
    if query.startswith("hello") or query.startswith("hi") or query.startswith("what's up"):
        return jsonify({
            "docs": "How can I help you? You can say 'Search' follows by area of research to run the expert search or start asking anything from wikipedia.",
            "type": "auto-text"
        })
    elif query.startswith("search"):
        # request = 
        return jsonify({
            "docs": query[6:],
            "type": "search"
        })
        # return redirect(url_for('search'), code=307)
    else:
        return jsonify({
            "docs": wiki_search(query),
            "type": "Wikipedia"
        })

def _get_doc_previews(doc_names,querytext):
    return list(map(lambda d: _get_preview(d,querytext), doc_names))

def format_string(matchobj):
    
    return '<b>'+matchobj.group(0)+'</b>'

def _get_preview(doc_name,querytext):
    preview = ""
    num_lines = 0
    preview_length = 2
    fullpath = app.datasetpath + "/" + doc_name

    with open(fullpath, 'r') as fp:
        while num_lines < preview_length:
            line = fp.readline()
            found_phrase = False
            if not line:
                break
            formatted_line = str(line.lower())
            for w in querytext.lower().split():

                (sub_str,cnt) = re.subn(re.compile(r"\b{}\b".format(w)),format_string,formatted_line)

                if cnt>0:
                    formatted_line = sub_str
                    found_phrase = True 

            if found_phrase:
                preview += formatted_line

                num_lines += 1
        fp.close()
 
    short_preview = ''
    prev_i = 0
    start = 0
    words = preview.split()
    cnt = 0
    i=0
   
    while i<len(words):
        

        
        if '<b>' in words[i]:
            start = min(i-prev_i,5)
            
            if  i-start>0:
                short_preview += '...'
            short_preview += ' '.join(words[i-start:i+5])
            i+=5
            prev_i = i
            cnt +=1
        else:
            i+=1
        if cnt==3:
            break


    return short_preview



if __name__ == '__main__':
    # environ = os.environ.get("APP_ENV")
    environ = 'development'
    dataconfig = json.loads(open("config.json", "r").read())
    app.dataenv = dataconfig[environ]
    app.rootpath = dataconfig[environ]["rootpath"]
    app.datasetpath = dataconfig[environ]['datasetpath']
    app.searchconfig = dataconfig[environ]['searchconfig']

    app.run(debug=True,threaded=True,host='localhost',port=8095)
