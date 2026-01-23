import unittest
from bs4 import BeautifulSoup

class TestBBRParser(unittest.TestCase):
    def setUp(self):
        self.html_content = """
        <div data-v-097f84e8="" class="sf-heading--no-underline sf-heading--center sf-heading"><h1 data-v-097f84e8="" class="sf-heading__title">
      Profiles on Burgundy
    </h1> <div data-v-097f84e8="" class="sf-heading__description display-none">
      
    </div></div>
    <div data-v-097f84e8="" class="read-time pre-title">
      Longer read • 8th January 2026
    </div>
    <div data-v-75b95245="" data-v-097f84e8="" class="authors single"><h5 data-v-75b95245="" class="authors-written-by">
    Written by
  </h5> <div data-v-75b95245="" class="authors-placeholder"><div data-v-6a543b32="" data-v-75b95245="" class="author-content"><div data-v-6a543b32="" class="author-content--placeholder"><picture data-v-49f02ffa="" data-v-6a543b32="" class="author-content--image"> <img data-v-49f02ffa="" src="https://media.bbr.com/i/bbr/Katie-Merry_9?fmt=auto&amp;qlt=default" alt="Katie-Merry_9" loading="lazy" fetchpriority="auto" class="image"></picture></div> <div data-v-6a543b32="" class="author-information"><div data-v-6a543b32="" class="author-information--content"><span data-v-6a543b32="" class="author-information--name body--default">
        Katie Merry
      </span> <span data-v-6a543b32="" class="author-information--description body--default">
        Junior Buyer
      </span></div></div></div></div></div>
      <div data-v-2870b34c="" class="rich-text-body-markdown"><div data-v-2870b34c=""><p data-v-2870b34c=""><span>
      I’m often thrown back to my mindset at the beginning of my career.
    </span></p></div></div>
        """

    def test_parse_article_details(self):
        soup = BeautifulSoup(self.html_content, 'html.parser')
        
        # Title
        title = soup.select_one('h1.sf-heading__title').get_text(strip=True)
        self.assertEqual(title, "Profiles on Burgundy")
        
        # Date
        date_text = soup.select_one('.read-time').get_text(strip=True)
        # Assuming we just want the raw string for now, or split by bullet
        self.assertIn("8th January 2026", date_text)
        
        # Author
        author = soup.select_one('.author-information--name').get_text(strip=True)
        self.assertEqual(author, "Katie Merry")
        
        # Content
        content_div = soup.select_one('.rich-text-body-markdown')
        content = content_div.get_text(strip=True)
        self.assertIn("I’m often thrown back", content)

if __name__ == '__main__':
    unittest.main()
