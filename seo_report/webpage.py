import bs4

import re
from six.moves.urllib import parse

from seo_report.stop_words import ENGLISH_STOP_WORDS
from seo_report.warnings import BADGES
from seo_report.warnings import WARNINGS

TOKEN_REGEX = re.compile(r'(?u)\b\w\w+\b')


class Webpage(object):
    url = None
    title = None
    description = None

    website_titles = {}
    website_descriptions = {}

    def __init__(self, page_url, html, website_titles, website_descriptions):
        self.url = page_url
        self.html = html
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
        soup = bs4.BeautifulSoup(self.html, "html.parser")

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

        # return the rendered results
        return self._render()

    def _analyze_title(self, doc):
        """
        Validate the title
        """
        self.title = t = ""
        if doc.title:
            self.title = t = doc.title.text

        # Avoid using extremely lengthy titles that are unhelpful to users
        length = len(t)
        if length == 0:
            self.warn(WARNINGS["TITLE_MISSING"], self.title)
            return
        elif length < 10:
            self.warn(WARNINGS["TITLE_TOO_SHORT"], self.title)
        elif length > 70:
            self.warn(WARNINGS["TITLE_TOO_LONG"], self.title)
        else:
            self.earned(BADGES["TITLE_LENGTH"], self.title)

        # Avoid using default or vague titles like "Untitled" or "New Page 1"
        if any(vague_words in t.lower()
               for vague_words in ['untitled', 'page']):
            self.warn(WARNINGS["TITLE_TOO_GENERIC"], self.title)
        else:
            self.earned(BADGES["TITLE_INFORMATIVE"], self.title)

        # Avoid stuffing unneeded keywords in your title tags
        title_words = self.grouped(self.tokenize(t))
        for word, count in title_words:
            if count > 3:
                self.warn(
                    WARNINGS["TITLE_KEYWORD_STUFFED"],
                    self.title)

        # Avoid choosing a title that has no relation to the content on the
        # page
        # TODO

        # Avoid using a single title tag across all of your site's pages or a
        # large group of pages
        if t in self.website_titles:
            self.warn(
                WARNINGS["TITLE_DUPLICATED"],
                '"{0}" previously used on pages: {1}'.format(
                    t, self.website_titles[t]))
        else:
            self.earned(BADGES["TITLE_UNIQUE"], self.title)
            self.website_titles[t] = self.url

    def _analyze_description(self, doc):
        """
        Validate the description
        """
        desc = doc.findAll('meta', attrs={'name': 'description'})

        self.description = d = ""
        if len(desc) > 0:
            self.description = d = desc[0].get('content', '')

        # calculate the length of the description once
        length = len(d)
        if length == 0:
            self.warn(WARNINGS["DESCRIPTION_MISSING"])
            return
        elif length < 140:
            self.warn(WARNINGS["DESCRIPTION_TOO_SHORT"], self.description)
        elif length > 255:
            self.warn(WARNINGS["DESCRIPTION_TOO_LONG"], self.description)
        else:
            self.earned(BADGES["DESCRIPTION_LENGTH"], self.description)

        # Avoid using generic descriptions like "This is a web page" or "Page
        # about baseball cards"
        if any(vague_words in d.lower()
               for vague_words in ['web page', 'page about']
               ):
            self.warn(WARNINGS["DESCRIPTION_TOO_GENERIC"], self.description)
        else:
            self.warn(BADGES["DESCRIPTION_INFORMATIVE"], self.description)

        # Avoid filling the description with only keywords
        desc_words = self.grouped(self.tokenize(d))
        for word, count in desc_words:
            if count > 3:
                self.warn(
                    WARNINGS["DESCRIPTION_KEYWORD_STUFFED"], self.description)

        # Avoid copying and pasting the entire content
        # of the document into the description meta tag
        # TODO

        # Avoid using a single description meta tag across all of your site's
        # pages or a large group of pages
        if d in self.website_descriptions:
            self.warn(WARNINGS["DESCRIPTION_DUPLICATED"],
                      '"{0}" previously used on pages: {1}'.format(
                d, self.website_descriptions[d]))
        else:
            self.website_descriptions[d] = self.url

    def _analyze_url_structure(self, doc):
        """
        Analyze URL Structure
        """

        parsed_url = parse.urlparse(self.url)
        path = parsed_url.path.split("/")

        # Avoid using lengthy URLs with unnecessary parameters and session IDs
        if len(self.url) > 100:
            self.warn(WARNINGS["URL_TOO_LONG"], self.url)

        # Avoid choosing generic page names like "page1.html"
        if any(vague_words in self.url.lower() for vague_words in ['page']):
            self.warn(WARNINGS["URL_TOO_GENERIC"], self.url)

        # Avoid using excessive keywords
        # like "baseball-cards-baseball-cards-baseballcards.htm"
        url_words = self.grouped(self.tokenize(path[-1]))
        for word, count in url_words:
            if count >= 2:
                self.warn(WARNINGS["URL_KEYWORD_STUFFED"], self.url)

        # Avoid having deep nesting of subdirectories like ".../dir1/dir2/dir3
        # /dir4/dir5/dir6/page.html"
        if len(path) > 3:
            self.warn(WARNINGS["URL_TOO_DEEP"], self.url)

        # Avoid using directory names that have no relation to the content in
        # them

        # Avoid having pages from subdomains and the root directory
        # access the same content
        #   if this is not the canonical page, then ignore it
        #   and only look at the canonical url
        canonical = doc.find("link", rel="canonical")
        if canonical:
            canonical_url = canonical['href']

            if canonical_url != self.url:
                # ignore this page, but ensure the canonical url is in our list
                self.warn(WARNINGS["URL_NOT_CANONICAL"], canonical_url)
            else:
                self.earned(BADGES["URL_CANONICAL"], self.url)

        # Avoid using odd capitalization of URLs
        if any(x.isupper() for x in self.url):
            self.warn(WARNINGS["URL_CAPITALIZED"], self.url)
        else:
            # Achievement: many users expect lower-case URLs and remember them
            # better
            self.earned(BADGES["URL_CORRECTLY_CASED"], self.url)

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

        # Avoid dumping large amounts of text on varying topics onto a page
        # without paragraph, subheading, or layout separation

        # Avoid inserting numerous unnecessary keywords aimed at
        # search engines but are annoying or nonsensical to users
        # (check percentage of keywords to content)

        pass

    def _analyze_anchors(self, doc):
        """
        Analyze Anchor Tags
        """
        anchors = doc.find_all('a', href=True)

        for tag in anchors:
            tag_href = tag['href']
            tag_text = tag.text.lower().strip()

            image_link = tag.find('img')

            if image_link is not None:
                # Ensure the image uses an Alt tag
                if len(image_link.get('alt', '')) == 0:
                    self.warn(WARNINGS["IMAGE_LINK_ALT_MISSING"], tag_href)
                else:
                    self.earned(BADGES["IMAGE_LINK_ALT"],
                                image_link.get('alt', ''))

            else:
                # Ensure title tags or the text are used in Anchors
                # Avoid writing long anchor text, such as a lengthy sentence or
                # short paragraph of text
                if len(tag.get('title', '')) == 0 and len(tag_text) == 0:
                    self.warn(WARNINGS["ANCHOR_TEXT_MISSING"], tag_href)
                elif len(tag_text) <= 3:
                    self.warn(WARNINGS["ANCHOR_TEXT_TOO_SHORT"], tag_text)
                elif len(tag_text) > 100:
                    self.warn(WARNINGS["ANCHOR_TEXT_TOO_LONG"], tag_text)

                # Avoid writing generic anchor text like "page", "article", or
                # "click here"
                if any(vague_words in tag_text.lower()
                       for vague_words in ['click here', 'page', 'article']):
                    self.warn(WARNINGS["ANCHOR_TEXT_TOO_GENERIC"], tag_text)

            if len(tag_href) > 100:
                self.warn(WARNINGS["ANCHOR_HREF_TOO_LONG"], tag_href)

            # Avoid using text that is off-topic or has no relation to the
            # content of the page linked to

            # Avoid using the page's URL as the anchor text in most cases
            if tag_text == tag_href:
                self.warn(WARNINGS["ANCHOR_HREF_EQUALS_TEXT"], tag_text)

            # Avoid comment spam to external websites
            if len(parse.urlparse(tag_href).netloc) > 0:
                if self.url not in tag_href:
                    if tag.get('rel') is None \
                       or 'nofollow' not in tag.get('rel'):
                        self.warn(WARNINGS["ANCHOR_NO_FOLLOW"], tag_href)
                    else:
                        self.earned(BADGES["ANCHOR_NO_FOLLOW"], tag_href)

    def _analyze_images(self, doc):
        """
        Verifies that each img has an alt and title
        """
        images = doc.find_all('img')

        for image in images:
            src = image.get('src', image.get('data-src', ''))

            if len(src) == 0:
                self.warn(WARNINGS["IMAGE_SRC_MISSING"], image)
            else:
                if len(image.get('alt', '')) == 0:
                    self.warn(WARNINGS["IMAGE_ALT_MISSING"], image)

                # Avoid using generic filenames like
                # "image1.jpg", "pic.gif", "1.jpg" when possible.
                # Some sites with thousands of images might consider
                # automating the naming of images
                # TODO

                # Avoid writing extremely lengthy filenames
                if len(src) > 15:
                    self.warn(WARNINGS["IMAGE_SRC_TOO_LONG"], src)

                # Avoid writing excessively long alt text that would be
                # considered spammy
                if len(image.get('alt', '')) > 40:
                    self.warn(WARNINGS["IMAGE_ALT_TOO_LONG"],
                              image.get('alt', ''))

                # Avoid using only image links for your site's navigation
                # TODO

    def _analyze_headings(self, doc):
        """
        Make sure each page has at least one header tag
        """
        h1tags = doc.find_all('h1')

        self.headers = []
        for h in h1tags:
            self.headers.append(h.text)

        if len(h1tags) == 0:
            self.warn(WARNINGS["H1_ONE_PER_PAGE"], self.headers)
        else:
            self.earned(BADGES["H1_ONE_PER_PAGE"], self.headers)

        # Avoid placing text in heading tags that wouldn't be helpful
        # in defining the structure of the page
        # TODO

        # Avoid using heading tags where other tags like <em> and <strong>
        # may be more appropriate
        # TODO

        # Avoid erratically moving from one heading tag size to another
        # TODO

        # Avoid excessively using heading tags throughout the page
        # TODO

        # Avoid putting all of the page's text into a heading tag
        # TODO

        # Avoid using heading tags only for styling text
        # and not presenting structure
        # TODO

    def _analyze_keywords(self, doc):

        # The Keywords Metatag should be avoided as they are a spam indicator
        # and no longer used by Search Engines
        kw_meta = doc.findAll('meta', attrs={'name': 'keywords'})

        if len(kw_meta) > 0:
            self.warn(WARNINGS["KEYWORDS_META"], kw_meta)

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
            self.warn(WARNINGS["WORDCOUNT_TOO_SHORT"],
                      u"You have {0} words.".format(count))
        else:
            self.earned(BADGES["WORDCOUNT"],
                        u"You have {0} words.".format(count))

    def _analyze_backlinks(self, doc):
        pass

    def _analyze_social(self, doc):
        # Facebook, Twitter, Pinterest, GooglePlus, Instagram
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

    def warn(self, message, value=None):
        self.issues.append(
            {
                "warning": message,
                "value": value
            }
        )

    def earned(self, message, value=None):
        self.achieved.append(
            {
                "achievement": message,
                "value": value
            }
        )

    def visible_tags(self, element):
        non_visible_elements = [
            'style', 'script', '[document]',
            'head', 'title', 'meta']

        if element.parent.name in non_visible_elements:
            return False
        elif isinstance(element, bs4.element.Comment):
            return False

        return True

    def tokenize(self, rawtext):
        return [
            word
            for word in TOKEN_REGEX.findall(rawtext.lower())
            if word not in ENGLISH_STOP_WORDS
        ]

    def grouped(self, token_list):
        grouped_list = {}
        for word in token_list:
            if word in grouped_list:
                grouped_list[word] += 1
            else:
                grouped_list[word] = 1

        grouped_list = sorted(grouped_list.items(),
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
