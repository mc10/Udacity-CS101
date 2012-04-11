import urllib

def get_page(url):
    try:
        return urllib.urlopen(url).read()
    except:
        return ""
    
def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1: 
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    words = content.split()
    for word in words:
        add_to_index(index, word, url)
        
def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None
    
def crawl_web(seed): # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    graph = {}  # <url>, [list of pages it links to]
    index = {} 
    while tocrawl: 
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            union(tocrawl, outlinks)
            crawled.append(page)
    return index, graph

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank += d * (ranks[node] / len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks

def lucky_search(index, ranks, keyword):
    pages = lookup(index, keyword)
    if not pages:
        return None
    best_page = pages[0]
    for candidate in pages:
        if ranks[candidate] > ranks[best_page]:
            best_page = candidate
    return best_page

def quicksort_pages(pages, ranks):
    if not pages or len(pages) <= 1:
        return pages
    else:
        pivot = ranks[pages[0]] # find pivot
        worse = []
        better = []
        for page in pages[1:]:
            if ranks[page] <= pivot:
                worse.append(page)
            else:
                better.append(page)
        return quicksort_pages(better, ranks) + [pages[0]] + quicksort_pages(worse, ranks)

def ordered_search(index, ranks, keyword):
    pages = lookup(index, keyword)
    return quicksort_pages(pages, ranks)

## TESTS BELOW THIS LINE ##
    
index, graph = crawl_web('http://udacity.com/cs101x/urank/index.html')
ranks = compute_ranks(graph)
print lucky_search(index, ranks, 'the')
print ordered_search(index, ranks, 'the')[0]
print ordered_search(index, ranks, 'Hummus')[0]