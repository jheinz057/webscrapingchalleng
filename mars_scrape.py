import datetime
    #import dependencies
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pymongo


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    mars_data = {}


    # ### NASA Mars News
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'

    # Retrieve page with the requests module
    response = requests.get(url)

    # Examine the results, then determine element that contains sought info
    soup = bs(response.text, 'html.parser')

    # Print all ten headlines
    headings = soup.find_all('div', class_="content_title")
    # A blank list to hold the headlines
    headlines = []
    # Loop over headlines and append
    for heading in headings:
        headlines.append(heading.a.get_text(strip=True)) 

    #grabbing news urls
    news_urls = soup.find_all('div', class_="content_title")
    news_links = []
    for link in news_urls:
        news_links.append(("https://mars.nasa.gov")+link.a['href'])

    #grabbing news descriptions
    descs = soup.find_all('div', class_="rollover_description_inner")
    descriptions = []
    for desc in descs:
            descriptions.append(desc.get_text(strip=True))


    # ### JPL Mars Space Images - Featured Image
    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url2)

    response = requests.get(url2)
    soup = bs(response.text, 'html.parser')

    big_images = soup.find_all('li', class_='slide')
    featured_image_url = []

    #append beginning of url to scraped url
    for big_image in big_images:
        try:
            featured_image_url.append(f"https://www.jpl.nasa.gov{big_image.a['data-fancybox-href']}")
        except:
            print("Scraping Complete! :)")


    # ### Mars Weather
    url3 = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url3)

    response3 = requests.get(url3)
    soup3 = bs(response3.text, 'html.parser')

    weather_updates=[]
    tweet_times=[]
    #locate the information within the html
    weather_tweets = soup3.find_all('div', class_='js-tweet-text-container')
    weather_times = soup3.find_all('span', class_='_timestamp')

    #find and append the tweet
    for tweet in weather_tweets:
        try:
            weather_updates.append(tweet.p.get_text(strip=True))
            tweet.a.extract()
        except:
            print("Scraping Complete! :)")

    #find and append the timestamp         
    for time in weather_times:
        try:
            tweet_times.append(time.get('data-time-ms'))
        except:
            print("Scraping Complete! :)")
            
    #fixing tweet times to be in date time format
    tweet_times_dt = []
    for tweet in tweet_times:
        your_dt = datetime.datetime.fromtimestamp(int(tweet)/1000)
        tweet_times_dt.append(your_dt.strftime("%Y-%m-%d %H:%M:%S"))

    #removing final url from tweet
    weather_updates_fixed = []
    for update in weather_updates:
        nopic = update.split('pic.twitter')[0]
        weather_updates_fixed.append(nopic)

    #zip tweet and timestamp together
    mars_tweets = [{'tweet': b, 'time': c} for b, c in zip(weather_updates_fixed, tweet_times_dt)]


    # ### Mars Facts
    url="https://space-facts.com/mars/"
    tables = pd.read_html(url)
    mars_df=tables[0]

    #scrape the table to html
    mars_df.to_html('mars_data.html',index=False)


    # ### Mars Hemispheres

    url4="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url4)

    response4 = requests.get(url4)
    soup4 = bs(response4.text, 'html.parser')

    import re
    links = []
    img_alt = []
    image_alts=[]
    for link in soup4.findAll('a',href=re.compile("enhanced")):
        try:
            links.append(link.get('href'))
            print(links)
        except:
            print("Scraping Complete! :)")
            
    for name in soup4.findAll('img',alt=re.compile("Enhanced")):
        try:
            img_alt.append(name.get('alt'))
            for i in img_alt:
                i.replace(' Enhanced thumbnail', '')
        except:
            print("Scraping Complete! :)")  
    print(img_alt)
    for img in img_alt:
        img2 = img.replace(" Enhanced thumbnail",'')
        image_alts.append(img2)
        

    final_links=[]

    #create a link with original url and path
    for link in links:
        final_links.append(f"https://astrogeology.usgs.gov{link}")
    final_links

    #loop through each link to get the full size image location
    fullsize_image=[]
    for link in final_links:
        response5 = requests.get(link)
        soup5 = bs(response5.text, 'html.parser')
        
        for image in soup5.find_all('a',href=re.compile("full.jpg")):
            try:
                fullsize_image.append(image.get('href'))
            except:
                print("Scraping Complete! :)")

    #zip image and title to one
    hemisphere_image_urls = [{'title': a, 'img_url': f} for a, f in zip(image_alts, fullsize_image)]


    #create a dictionary of all of the items
    mars_data["mars_news_headlines"] = headlines
    mars_data["mars_news_desc"] = descriptions
    mars_data["mars_news_link"] = news_links
    mars_data["mars_image"] = featured_image_url
    mars_data["mars_tweets"] = mars_tweets
    mars_data["mars_hemispheres"] = hemisphere_image_urls

    return mars_data


if __name__ == "__main__":
    print(scrape())
# If running as script, print scraped data
