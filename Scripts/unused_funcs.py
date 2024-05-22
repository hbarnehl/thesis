# My go at building a scraper with rotating headers and proxies

def rotate_scrape(page):
    proxies, users = get_proxies()
    last = time()
    i = 0
    url = articles[0][x]
    title = articles[1][x]
    text = scraping(url, i, last, proxies, users)
    canal13_list.append({"url": url, "title": title, "text": text})
    
def scraping(url, i, last, proxies, users):
    i = i+1
    if i % 200 == 0: logger.warning(f"Status: url {i}")
    if time()-last > 1800:
        proxies, users = get_proxies()
    tries = 0
    text = None
    while (tries < 3) & (text == None):
        tries = tries +1
        proxy = next(proxies)
        user = next(users)
        headers = requests.utils.default_headers()
        headers['User-Agent'] = user
        try:
            source = requests.get(url, headers=headers, proxies={"https": proxy}).text
            tree = html.fromstring(source)
            text = " ".join([l.text_content() for l in tree.xpath("//div[@class='entry-content']/p")])
        except Exception as e:
            logger.error(f"{url}: {e}")
            if tries == 3:
                print(f"skip {url}")
    return text

def get_proxies():  
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = html.fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = i.xpath('.//td[1]/text()')[0] + ":" + i.xpath('.//td[2]/text()')[0]
            proxies.add(proxy)
    
    url = 'https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&protocols=https&anonymityLevel=elite&anonymityLevel=anonymous'
    response = requests.get(url)
    data = response.json()['data']
    for x in data:
        proxy = x["ip"]+":"+x["port"]
        proxies.add(proxy)
    
    ua = UserAgent()
    users = set()
    for i in range(30):
        user = ua.random
        users.add(user)
        
    proxies = cycle(proxies)
    users = cycle(users)
        
    return proxies, users

# scraper specifically for RadioYa, but they blocked me everywhere, so whatever
def scrape_ya(i):
    logger.info(f'Working on {name}.')
    # report on status at every ten pages
    if i % 10 == 0: logger.info(f"Status {name}: page {i}")
    try:
        url = baseurl+str(i)
        source = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
        tree = html.fromstring(source)
        if isinstance(outlet['titlepath'] , list):
            links = [outlet['prefix'] + l.attrib['href'] for l in (tree.xpath(outlet["linkpath"][0]) + tree.xpath(outlet["linkpath"][1]))]
            titles = [l.text for l in (tree.xpath(outlet["titlepath"][0]) + tree.xpath(outlet["titlepath"][1]))]
        else:
            links = [outlet['prefix'] + l.attrib['href']for l in tree.xpath(outlet["linkpath"])]
            titles = [l.text for l in tree.xpath(outlet["titlepath"])]
        [linklist.append(x) for x in links]
        [titlelist.append(x) for x in titles]
    except Exception as e:
        logger.error(f"Error with {name} at page {i}:")
        logger.error(e)
    sleep(randint(3, 6))

    combined = [linklist, titlelist]
    with open(f'{name}-links-titles.pkl', 'wb') as f:
        pickle.dump(combined, f)