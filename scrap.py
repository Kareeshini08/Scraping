import csv
import requests
from bs4 import BeautifulSoup

def scrape_product_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_details = {}

    # Extracting additional product details
    product_details['URL'] = url

    # Extract ASIN
    asin_element = soup.find('th', text='ASIN')
    if asin_element:
        asin_value = asin_element.find_next('td')
        product_details['ASIN'] = asin_value.get_text(strip=True)
    else:
        div_element = soup.find('div', {'id': 'productDetails_feature_div'})
        if div_element:
            asin_li = div_element.find('li', text=lambda text: 'ASIN' in text)
            if asin_li:
                asin = asin_li.find('span', {'class': 'a-text-bold'}).find_next_sibling('span').text.strip()
                product_details['ASIN'] = asin

    # Extract product description
    description_element = soup.find('div', {'id': 'productDescription'})
    if description_element:
        description = description_element.find('p')
        if description:
            product_details['Description'] = description.get_text(strip=True)

    # Extract manufacturer
    manufacturer_element = soup.find('th', text='Manufacturer')
    if manufacturer_element:
        manufacturer_value = manufacturer_element.find_next('td')
        product_details['Manufacturer'] = manufacturer_value.get_text(strip=True)
    else:
        div_element = soup.find('div', {'id': 'productDetails_feature_div'})
        if div_element:
            manufacturer_li = div_element.find('li', text=lambda text: 'Manufacturer' in text)
            if manufacturer_li:
                manufacturer = manufacturer_li.find('span', {'class': 'a-text-bold'}).find_next_sibling(
                    'span').text.strip()
                product_details['Manufacturer'] = manufacturer

    return product_details


def scrape_amazon_products(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    # Extracting product details
    listings = soup.find_all('div', {'data-component-type': 's-search-result'})

    for listing in listings:
        product = {}

        # Extract product URL
        link = listing.find('a', {'class': 'a-link-normal s-no-outline'})
        if link:
            product_url = 'https://www.amazon.in' + link['href']
            product_details = scrape_product_details(product_url)
            product.update(product_details)

        # Extract product name
        name = listing.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
        if name:
            product['Name'] = name.get_text(strip=True)

        # Extract product price
        price = listing.find('span', {'class': 'a-price-whole'})
        if price:
            product['Price'] = price.get_text(strip=True)

        # Extract rating and number of reviews
        rating = listing.find('span', {'class': 'a-icon-alt'})
        reviews = listing.find('span', {'class': 'a-size-base'})
        if rating and reviews:
            product['Rating'] = rating.get_text(strip=True)
            product['Reviews'] = reviews.get_text(strip=True)

        products.append(product)

    return products


base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}'

all_products = []

for page in range(1, 21):
    url = base_url.format(page)
    products = scrape_amazon_products(url)
    all_products.extend(products)
    if len(all_products) >= 200:
        break

# Exporting scraped data to CSV
csv_file = 'amazon_products.csv'

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['URL', 'Name', 'Price', 'Rating', 'Reviews', 'ASIN', 'Description', 'Manufacturer']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_products)

print('Scraped data has been exported to', csv_file)