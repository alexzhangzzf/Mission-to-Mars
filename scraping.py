# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)   

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemis_data": hemi_data(browser)
    }
 
    #stop webdriver and return data
    browser.quit()
    return data

#scrape news title and paragraphs
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p


# Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        #find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

#Mars Facts
def mars_facts():
    try:
        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    #assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    #convert dataframe to HTML format, add bootstrap
    return df.to_html()

#scrape hemisphere data
def hemi_data(browser):

    # Use browser to visit the URL 
    hemi_url = 'https://marshemispheres.com/'
    browser.visit(hemi_url)

    # get the list of links for four hemispheres
    a_elems = browser.find_by_css('a.product-item')
    hemi_links = []
    for e in a_elems:
        if e.find_by_tag('img'):
            hemi_links.append(e['href'])

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    for link in hemi_links:
        browser.visit(link)
        title = browser.find_by_css('h2.title').text
        img_url= browser.links.find_by_text('Sample').first['href']
        hemispheres = {
            'img_url': img_url,
            'title': title
                    }
        hemisphere_image_urls.append(hemispheres)

    # return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls



if __name__ == "__main__":

    #if running as script, print scraped data
    print(scrape_all())
