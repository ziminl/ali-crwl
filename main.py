


import asyncio
import pandas as pd
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
from requests_html import HTMLSession
session = HTMLSession()
df = pd.DataFrame(columns=["sold", "price", "store", "evaluate"])
page_no = 2



url = "https://www.aliexpress.com/category/509/cellphones-telecommunications.html"



async def scrape_page(url):
    # Open a headless browser using Pyppeteer
    browser = await launch(headless=True)
    page = await browser.newPage()
    
    try:
        await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 60000})
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2);")
        await page.waitFor(2000)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await page.waitFor(2000)
        content = await page.content()
        rendered_session = HTMLSession()
        rendered_session.browser = browser
        r = rendered_session.get("data:text/html," + content)
        products = r.html.find(".manhattan--content--1KpBbUi")
        
        for product in products:
            prod_dic = {}
            try:
                sold = product.find(".manhattan--trade--2PeJIEB", first=True).text
                price = product.find(".manhattan--price-sale--1CCSZfK", first=True).text
                store = product.find(".cards--storeLink--1_xx4cD", first=True).text
                evaluate = product.find(".manhattan--evaluation--3cSMntr", first=True).text
                
                prod_dic = {
                    "sold": sold,
                    "price": price,
                    "store": store,
                    "evaluate": evaluate
                }
              
            except AttributeError:
                pass
            df.loc[len(df)] = prod_dic
            
        await rendered_session.close()
        await browser.close()
        
    except TimeoutError:
        print("Page loading timed out.")
        await browser.close()

loop = asyncio.get_event_loop()
tasks = []

for page in range(1, page_no + 1):
    link = f"{url}?page={page}"
    tasks.append(scrape_page(link))

loop.run_until_complete(asyncio.gather(*tasks))
#print(df)



df.to_csv("aliexpress.csv")


