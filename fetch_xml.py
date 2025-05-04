import requests
from bs4 import BeautifulSoup

def fetch_reviews():
    # Define the URL of your Laravel endpoint
    url = 'http://127.0.0.1:8000/reviews/xml'

    try:
        # Send a GET request to the Laravel endpoint
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse HTML content (transformed XML)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract data
            rows = soup.find_all('tr')[1:]  # skip header row
            reviews = []
            
            for row in rows:
                cols = row.find_all('td')
                user = cols[0].text.strip()
                material = cols[1].text.strip()
                rating = cols[2].text.strip()
                comment = cols[3].text.strip()
                reported = cols[4].text.strip()
                
                review = {
                    'user': user,
                    'material': material,
                    'rating': rating,
                    'comment': comment,
                    'reported': reported
                }
                reviews.append(review)
                print(f"User: {user}, Material: {material}, Rating: {rating}, Comment: {comment}, Reported: {reported}")
            
            return reviews
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    fetch_reviews() 