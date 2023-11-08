import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib import robotparser
from bs4 import BeautifulSoup
from collections import defaultdict

q1 = set()
q2 = {"page":"", "count":0}
q3 = defaultdict(int)
q4 = defaultdict(int)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if url != resp.url: #redirect
        url = resp.url
    links = []
    if resp.status == 200:
        content = resp.raw_response.content
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        if len(text.split()) < 100: #low information
            return []
        q1f(url)
        q2f(url,text)
        q3f(text)
        q4f(url)
        for link in soup.find_all("a"):
            abs_url = urljoin(url,link.get("href")) # absolute url
            links.append(abs_url.split("#")[0])
    return links

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if url in q1:
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.hostname == None:
            return False
        if not (robot_check(parsed) and domain_check(parsed) and trap_check(parsed)):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|calender|php)", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

checked = dict()

def robot_check(parsed):
    global checked
    robot_file = parsed.hostname + "/robots.txt"
    if robot_file not in checked:
        robot = robotparser.RobotFileParser()
        robot.set_url(robot_file)
        try:
            robot.read()
        except Exception:
            return True
        checked[robot_file] = robot.can_fetch("*",robot_file)
        return robot.can_fetch("*", robot_file)
    else:
        return checked[robot_file]

def domain_check(parsed):
    if parsed.hostname == None:
        return False
    for domain in [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]:
        if domain in parsed.hostname:
            return True
    return False

def trap_check(parsed):
    seg = parsed.path.split('/')
    for i in range(len(seg) - 1):
        if seg[i] == seg[i+1]:
            return False
    return True

def q1f(url):
    global q1
    if url not in q1:
        q1.add(url)

def q2f(url, text):
    global q2
    length = len(text.split())
    if length > q2["count"]:
        q2["page"] = url
        q2["count"] = length

stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
"before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing",
"don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll",
 "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
  "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only",
   "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd",
     "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
      "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why",
       "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]

def q3f(text):
    tokens = []
    text = text.lower()
    temp = ''
    for c in text:
        if c.isalnum():
            temp += c
        else:
            if temp != "":
                if temp not in stopwords and len(temp) > 1:
                    tokens.append(temp)
            temp = ''
        if c == "":
            break
    freq = dict()
    for token in tokens:
        if token not in freq:
            freq[token] = 1
        else:
            freq[token] += 1
    global q3
    for token, count in freq.items():
        q3[token] += count

def q4f(url):
    global q4
    parsed = urlparse(url)
    if ".ics.uci.edu" in parsed.hostname:
        host = parsed.scheme + "://" + parsed.hostname
        q4[host] += 1


def report():
    with open("report.txt", 'w') as myfile:
        myfile.write(f"Total number of unique pages is {str(len(q1))} \n")
        myfile.write("Longest page is " + q2["page"] + ". Total word count is " + str(q2["count"]) + "\n")
        myfile.write("50 most common words:\n")
        sort_dict = sorted(q3.items(), key=lambda x: x[1], reverse=True)
        for k, v in sort_dict[:50]:
            myfile.write(k + " " + str(v) + "\n")
        myfile.write("Subdomains's unique pages(ordered alphabetically):\n")
        for k, v in sorted(q4.items(), key=lambda x: x[0]):
            myfile.write(k + " " + str(v) + "\n")


