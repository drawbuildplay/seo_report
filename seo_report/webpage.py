import bs4

import re
import requests
import urlparse

# Most Search Engines do not consider extremely common words in order to save disk space or to speed up search results. These filtered words are known as 'Stop Words'.
# http://www.webconfs.com/stop-words.php
ENGLISH_STOP_WORDS = frozenset(["able", "about", "above", "abroad", "according", "accordingly", "across", "actually", "adj", "after", "afterwards", "again", "against", "ago", "ahead", "ain't", "all", "allow", "allows", "almost", "alone", "along", "alongside", "already", "also", "although", "always", "am", "amid", "amidst", "among", "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "are", "aren't", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "back", "backward", "backwards", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "both", "brief", "but", "by", "came", "can", "cannot", "cant", "can't", "caption", "cause", "causes", "certain", "certainly", "changes", "clearly", "c'mon", "co", "co.", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn't", "course", "c's", "currently", "dare", "daren't", "definitely", "described", "despite", "did", "didn't", "different", "directly", "do", "does", "doesn't", "doing", "done", "don't", "down", "downwards", "during", "each", "edu", "eg", "eight", "eighty", "either", "else", "elsewhere", "end", "ending", "enough", "entirely", "especially", "et", "etc", "even", "ever", "evermore", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "fairly", "far", "farther", "few", "fewer", "fifth", "first", "five", "followed", "following", "follows", "for", "forever", "former", "formerly", "forth", "forward", "found", "four", "from", "further", "furthermore", "get", "gets", "getting", "given", "gives", "go", "goes", "going", "gone", "got", "gotten", "greetings", "had", "hadn't", "half", "happens", "hardly", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "here's", "hereupon", "hers", "herself", "he's", "hi", "him", "himself", "his", "hither", "hopefully", "how", "howbeit", "however", "hundred", "i'd", "ie", "if", "ignored", "i'll", "i'm", "immediate", "in", "inasmuch", "inc", "inc.", "indeed", "indicate", "indicated", "indicates", "inner", "inside", "insofar", "instead", "into", "inward", "is", "isn't", "it", "it'd", "it'll", "its", "it's", "itself", "i've", "just", "k", "keep", "keeps", "kept", "know", "known", "knows", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "let's", "like", "liked", "likely", "likewise", "little", "look", "looking", "looks", "low", "lower", "ltd", "made", "mainly", "make", "makes", "many", "may", "maybe", "mayn't", "me", "mean", "meantime", "meanwhile", "merely", "might", "mightn't", "mine", "minus", "miss", "more", "moreover", "most", "mostly", "mr", "mrs", "much", "must",
                                "mustn't", "my", "myself", "name", "namely", "nd", "near", "nearly", "necessary", "need", "needn't", "needs", "neither", "never", "neverf", "neverless", "nevertheless", "new", "next", "nine", "ninety", "no", "nobody", "non", "none", "nonetheless", "noone", "no-one", "nor", "normally", "not", "nothing", "notwithstanding", "novel", "now", "nowhere", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "on", "once", "one", "ones", "one's", "only", "onto", "opposite", "or", "other", "others", "otherwise", "ought", "oughtn't", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", "particular", "particularly", "past", "per", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provided", "provides", "que", "quite", "qv", "rather", "rd", "re", "really", "reasonably", "recent", "recently", "regarding", "regardless", "regards", "relatively", "respectively", "right", "round", "said", "same", "saw", "say", "saying", "says", "second", "secondly", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "since", "six", "so", "some", "somebody", "someday", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify", "specifying", "still", "sub", "such", "sup", "sure", "take", "taken", "taking", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "there'd", "therefore", "therein", "there'll", "there're", "theres", "there's", "thereupon", "there've", "these", "they", "they'd", "they'll", "they're", "they've", "thing", "things", "think", "third", "thirty", "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "till", "to", "together", "too", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "t's", "twice", "two", "un", "under", "underneath", "undoing", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "up", "upon", "upwards", "us", "use", "used", "useful", "uses", "using", "usually", "v", "value", "various", "versus", "very", "via", "viz", "vs", "want", "wants", "was", "wasn't", "way", "we", "we'd", "welcome", "well", "we'll", "went", "were", "we're", "weren't", "we've", "what", "whatever", "what'll", "what's", "what've", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "where's", "whereupon", "wherever", "whether", "which", "whichever", "while", "whilst", "whither", "who", "who'd", "whoever", "whole", "who'll", "whom", "whomever", "who's", "whose", "why", "will", "willing", "wish", "with", "within", "without", "wonder", "won't", "would", "wouldn't", "yes", "yet", "you", "you'd", "you'll", "your", "you're", "yours", "yourself", "yourselves", "you've", "zero"])

TOKEN_REGEX = re.compile(r'(?u)\b\w\w+\b')


class Webpage(object):
    url = None
    title = None
    description = None
    avoid = []
    achieved = []

    website_titles = {}
    website_descriptions = {}

    def __init__(self, page, website_titles, website_descriptions):
        self.url = page
        self.title = None
        self.description = None
        self.keywords = {}
        self.issues = []
        self.achieved = []

        self.website_titles = website_titles
        self.website_descriptions = website_descriptions

    def report(self):
        ''' 
        Analyze the Page
        '''
        resp = requests.get(self.url)

        if resp.ok:
            soup = bs4.BeautifulSoup(resp.content, "html.parser")

            # per page analysis
            self._analyze_title(soup)
            self._analyze_description(soup)
            self._analyze_url_structure(soup)
            self._analyze_content(soup)
            self._analyze_anchors(soup)
            self._analyze_images(soup)
            self._analyze_headings(soup)
            self._analyze_keywords(soup)
            self._analyze_wordcount(soup)
            self._analyze_backlinks(soup)
            self._analyze_social(soup)
            self._analyze_pagespeed(soup)
            self._analyze_sentiment(soup)

            # site wide analysis
            # self._analyze_crawlers(soup)
            # self._analyze_mobile(soup)
            # self._analyze_analytics(soup)

        elif resp.status_code == 404:
            self.warn(
                "Avoid having broken links in your sitemap or website: {0}".format(self.url))

        # return the rendered results
        return self._render()

    def _analyze_title(self, doc):
        """
        Validate the title
        """
        self.title = t = doc.title.text

        # Avoid using extremely lengthy titles that are unhelpful to users
        length = len(t)
        if length == 0:
            self.warn(u'Missing title tag')
            return
        elif length < 10:
            self.warn(u'Title tag is too short (less than 10 characters)')
        elif length > 70:
            self.warn(u'Title tag is too long (more than 70 characters)')
        else:
            self.earned(u'Title is a great length')

        # Avoid using default or vague titles like "Untitled" or "New Page 1"
        if any(vague_words in t.lower() for vague_words in ['untitled', 'page']):
            self.warn(u'Title is too vague')
        else:
            self.earned(u'Title is informative')

        # Avoid stuffing unneeded keywords in your title tags
        title_words = self.grouped(self.tokenize(t))
        for word, count in title_words:
            if count > 3:
                self.warn(
                    u"Avoid keyword stuffing in the title: {0}".format(t))

        # Avoid choosing a title that has no relation to the content on the
        # page
        # TODO

        # Avoid using a single title tag across all of your site's pages or a
        # large group of pages
        if t in self.website_titles:
            self.warn(u'Duplicate page title: {0} previously used at {1}'.format(
                t, self.website_titles[t]))
        else:
            self.earned(u'This page has a unique title tag')
            self.website_titles[t] = self.url

    def _analyze_description(self, doc):
        """
        Validate the description
        """
        d = ''
        desc = doc.findAll('meta', attrs={'name': 'description'})
        if len(desc) > 0:
            self.description = d = desc[0].get('content')

        # calculate the length of the description once
        length = len(d)
        if length == 0:
            self.warn(u'Description is missing.')
            return
        elif length < 140:
            self.warn(
                u'Description is too short (less than 140 characters): {0}'.format(d))
        elif length > 255:
            self.warn(
                u'Description is too long (more than 255 characters): {0}'.format(d))
        else:
            self.earned(
                u'Descriptions are important as Google may use them as page snippets.')

        # Avoid using generic descriptions like "This is a web page" or "Page
        # about baseball cards"
        if any(vague_words in d.lower() for vague_words in ['web page', 'page about']):
            self.warn(u'Description is too generic')
        else:
            self.earned(u'Description is informative')

        # Avoid filling the description with only keywords
        desc_words = self.grouped(self.tokenize(d))
        for word, count in desc_words:
            if count > 3:
                self.warn(
                    u"Avoid keyword stuffing in the description: {0}".format(d))

        # Avoid copying and pasting the entire content of the document into the description meta tag
        # TODO

        # Avoid using a single description meta tag across all of your site's
        # pages or a large group of pages
        if d in self.website_descriptions:
            self.warn(u'Duplicate description: {0} previously used at: {1}'.format(
                d, self.website_descriptions[d]))
        else:
            self.website_descriptions[d] = self.url

    def _analyze_url_structure(self, doc):
        """
        Analyze URL Structure
        """
        
        parsed_url = urlparse.urlparse(self.url)
        path = parsed_url.path.split("/")
        
        # Avoid using lengthy URLs with unnecessary parameters and session IDs
        if len(parsed_url.path) > 100:
            self.warn(u"Avoid using length URLs")
            
        # Avoid choosing generic page names like "page1.html"
        if any(vague_words in self.url.lower() for vague_words in ['page']):
            self.warn(u'Avoid choosing generic page names like "page1.html"')

        # Avoid using excessive keywords
        # like "baseball-cards-baseball-cards-baseballcards.htm"
        url_words = self.grouped(self.tokenize(path[-1]))
        for word, count in url_words:
            if count > 2:
                self.warn(
                    u"Avoid keyword stuffing in the url: {0}".format(self.url))

        # Avoid having deep nesting of subdirectories like ".../dir1/dir /dir
        # /dir4/dir5/dir6/page.html"
        if len(path) > 3:
            self.warn(u"Avoid deep nesting of subdirectories: {0}".format(parsed_url.path))
            
        # Avoid using directory names that have no relation to the content in
        # them

        # Avoid having pages from subdomains and the root directory access the same content
        #   if this is not the canonical page, then ignore it
        #   and only look at the canonical url
        canonical = doc.find("link", rel="canonical")
        if canonical:
            canonical_url = canonical['href']

            if canonical_url != self.url:
                # ignore this page, but ensure the canonical url is in our list
                self.warn("Only one version of a URL (Canonical URL) should be used to reach a document: {0}".format(
                    canonical_url))

        # Avoid using odd capitalization of URLs
        if any(x.isupper() for x in self.url):
            self.warn(
                u'Avoid using uppercase characters in the URL. Many users expect lower-case URLs and remember them better')
        else:
            # Achievement: many users expect lower-case URLs and remember them
            # better
            self.earned(
                u'URL is lowercase. Many users expect lower-case URLs and remember them better')

        # Avoid creating complex webs of navigation links, e.g. linking every
        # page on your site to every other page

        # Avoid going overboard with slicing and dicing your content (so that
        # it takes twenty clicks)

        # Avoid having a navigation based entirely on drop-down menus, images,
        # or animations

        # Avoid letting your HTML site map page become out of date with broken
        # links

        # Avoid allowing your 404 pages to be indexed in search engines

        # Avoid providing only a vague message like "Not found", "404", or no
        # 404 page at all

    def _analyze_content(self, doc):
        # Avoid bad spelling and bad grammar
        
        # Avoid dumping large amounts of text on varying topics onto a page without paragraph, subheading, or layout separation
        
        # Avoid inserting numerous unnecessary keywords aimed at search engines but are annoying or nonsensical to users
        # (check percentage of keywords to content)
        
        
        pass

    def _analyze_anchors(self, doc):
        """
        Analyze Anchor Tags
        """
        anchors = doc.find_all('a', href=True)

        for tag in anchors:
            tag_href = tag['href'].encode('utf-8')
            tag_text = tag.text.lower().strip()

            image_link = tag.find('img')

            if image_link is not None:
                # Ensure the image uses an Alt tag
                if len(image_link.get('alt', '')) == 0:
                    self.warn(
                        'Image link missing Alt tag: {0}'.format(tag_href))

            else:
                # Ensure title tags or the text are used in Anchors
                # Avoid writing long anchor text, such as a lengthy sentence or
                # short paragraph of text
                if len(tag.get('title', '')) == 0 and len(tag_text) == 0:
                    self.warn(
                        'Anchor missing title tag or text: {0}'.format(tag_href))
                elif len(tag_text) < 3:
                    self.warn(
                        'Anchor text too short (less than 3 characters): {0}'.format(tag_text))
                elif len(tag_text) > 80:
                    self.warn(
                        'Anchor text too long (more than 80 characters): {0}'.format(tag_text))

                # Avoid writing generic anchor text like "page", "article", or
                # "click here"
                if any(vague_words in tag_text.lower() for vague_words in ['click here', 'page', 'article']):
                    self.warn(
                        'Anchor text contains generic text: {0}'.format(tag_text))

            # Avoid using text that is off-topic or has no relation to the
            # content of the page linked to

            # Avoid using the page's URL as the anchor text in most cases
            if tag_text == tag_href:
                self.warn(
                    'Avoid using the page URL as the anchor text: {0}'.format(tag_text))

            # Avoid comment spam to external websites
            if self.url not in tag_href and 'rel' in tag and "nofollow" not in tag['rel']:
                self.warn(
                    'Avoid passing your reputation to non-relevant websites: {0}'.format(tag_href))

    def _analyze_images(self, doc):
        """
        Verifies that each img has an alt and title
        """
        images = doc.find_all('img')

        for image in images:
            src = ''
            if 'src' in image:
                src = image['src']
            elif 'data-src' in image:
                src = image['data-src']
            else:
                src = image

            if len(image.get('alt', '')) == 0:
                self.warn('Image missing alt tag: {0}'.format(src))

            # Avoid using generic filenames like "image1.jpg", "pic.gif", "1.jpg" when possible.
            # Some sites with thousands of images might consider automating the
            # naming of images
            # TODO

            # Avoid writing extremely lengthy filenames
            if len(src) > 15:
                self.warn(
                    "Avoid writing extremely lengthy filenames: {0}".format(src))

            # Avoid writing excessively long alt text that would be considered
            # spammy
            if len(image.get('alt', '')) > 40:
                self.warn("Avoid writing excessively long alt text that would be considered spammy: {0}".format(
                    image.get('alt', '')))

            # Avoid using only image links for your site's navigation
            # TODO

    def _analyze_headings(self, doc):
        """
        Make sure each page has at least one header tag
        """
        htags = doc.find_all('h1')

        self.headers = []
        for h in htags:
            self.headers.append(h.text)

        if len(htags) == 0:
            self.warn('Each page should have at least one h1 tag')

        # Avoid placing text in heading tags that wouldn't be helpful in defining the structure of the page
        # TODO

        # Avoid using heading tags where other tags like <em> and <strong> may be more appropriate
        # TODO

        # Avoid erratically moving from one heading tag size to another
        # TODO

        # Avoid excessively using heading tags throughout the page
        # TODO

        # Avoid putting all of the page's text into a heading tag
        # TODO

        # Avoid using heading tags only for styling text and not presenting structure
        # TODO

    def _analyze_keywords(self, doc):

        # The Keywords Metatag should be avoided as they are a spam indicator
        # and no longer used by Search Engines
        kw_meta = doc.findAll('meta', attrs={'name': 'keywords'})

        if len(kw_meta) > 0:
            self.warn(
                'The Keywords Metatag should be avoided as they are a spam indicator and no longer used by Search Engines: {0}'.format(k))

        # Detect the most popular keywords used on the page
        self.keywords = self._get_keywords(doc)

        # we only care about the top 5 keywords
        del self.keywords[5:]

    def _analyze_wordcount(self, doc):
        # Word Count: We have known for some time that Google shows a
        # preference for longer, more comprehensive content. According to the
        # report, the average word count for top-ranking content is in the
        # range of 1,140-1,285 words. This is up from 902 words in 2014. When
        # creating content, focus on providing comprehensive coverage of your
        # topic, rather than writing shorter content that only brushes the
        # surface of your topic

        page_content = self._get_keywords(doc)

        # calculate total number of words used (ignoring stop words)
        count = 0
        for word, freq in page_content:
            count += freq

        if count < 1140:
            self.warn(
                u"The average word count for top-ranking content is 1,140 - 1,285 words.  You have {0} words.".format(count))
        else:
            self.achieved(
                u"You have provided great comprehensive coverage of your topic with {0} words.".format(count))

    def _analyze_crawlers(self, doc):
        # robots.txt present
        resp = requests.get(self.url + "/robots.txt")
        if resp.ok:
            self.achieved(
                u"robots.txt detected.  This helps search engines navigate pages that should be indexed")
        else:
            self.warn(
                u"robots.txt is missing.  A 'robots.txt' file tells search engines whether they can access and therefore crawl parts of your site")

    def _analyze_mobile(self, doc):
        pass

    def _analyze_backlinks(self, doc):
        pass

    def _analyze_social(self, doc):

        # Facebook, Twitter, Pinterest, GooglePlus, Instagram
        pass

    def _analyze_analytics(self, doc):
        # Use Google Analytics or Omniture etc

        pass

    def _analyze_pagespeed(self, doc):
        # Page load times should be < X seconds

        # Are you using a CDN

        # Are your CSS and JS files minimized

        pass

    def _analyze_sentiment(self, doc):
        # Analyze the sentiment of the text used on the page
        # http://textblob.readthedocs.io/en/dev/

        # Avoid negative emotion when conveying your product and services

        pass

    def _render(self):
        '''
        Render the result
        '''

        # iterate the keywords for returning
        keywords_result = []

        for word, count in self.keywords:
            kw = {
                "keyword": word,
                "frequency": count,
                "in_title": word in self.title.lower(),
                "in_description": word in self.description.lower(),
                "in_header": word in self.headers
            }
            keywords_result.append(kw)

        result = {
            "url": self.url,
            "keywords": keywords_result,
            "issues": self.issues,
            "achieved": self.achieved,
            "title": self.title,
            "description": self.description
        }

        return result

    def warn(self, message):
        self.issues.append(message)

    def earned(self, message):
        self.achieved.append(message)

    def visible_tags(self, element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'meta']:
            return False
        elif isinstance(element, bs4.element.Comment):
            return False

        return True

    def tokenize(self, rawtext):
        return [word for word in TOKEN_REGEX.findall(rawtext.lower()) if word not in ENGLISH_STOP_WORDS]

    def grouped(self, token_list):
        grouped_list = {}
        for word in token_list:
            if word in grouped_list:
                grouped_list[word] += 1
            else:
                grouped_list[word] = 1

        grouped_list = sorted(grouped_list.iteritems(),
                              key=lambda x: x[1], reverse=True)
        return grouped_list

    def _get_keywords(self, doc):
        keywords = {}
        text_elements = filter(self.visible_tags, doc.findAll(text=True))
        page_text = ''
        for element in text_elements:
            page_text += element.lower() + ' '

        tokens = self.tokenize(page_text)
        keywords = self.grouped(tokens)

        return keywords
