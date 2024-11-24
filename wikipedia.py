import requests

# # main url:- https://en.wikipedia.org/w/api.php?action=query&titles=anjuna&prop=pageimages&format=json&pithumbsize=500

# =====================================================================================================

#
# def get_wikipedia_image(destination):
#     # Wikipedia API endpoint
#     url = f"https://en.wikipedia.org/w/api.php"
#
#     # API parameters
#     params = {
#         'action': 'query',
#         'titles': destination,
#         'prop': 'pageimages',
#         'format': 'json',
#         'pithumbsize': 500
#     }
#
#     # Make a request to Wikipedia API
#     response = requests.get(url, params=params)
#
#     if response.status_code == 200:
#         data = response.json()
#         # print(data)
#
#         # Extract the page information
#         pages = data.get("query", {}).get("pages", {})
#
#         for page_id, page_info in pages.items():
#             if "thumbnail" in page_info:
#                 # Get the image source URL from the thumbnail
#                 image_source = page_info["thumbnail"]["source"]
#                 return image_source
#             else:
#                 return "Error: No image found for the destination."
#     else:
#         return f"Error: Unable to fetch data (status code {response.status_code})"



# =====================================================================================================



def get_wikipedia_image_for_specific_destination(query):
  url_search = "https://en.wikipedia.org/w/api.php"
  search_params = {
    'action': 'query',
    'list': 'search',
    'srsearch': query,
    'format': 'json',
    'utf8': 1,
  }

  try:
    # Step 1: Search for the destination on Wikipedia
    search_response = requests.get(url_search, params=search_params)
    search_response.raise_for_status()
    search_data = search_response.json()

    if search_data['query']['search']:
      # Get the best match title from search results
      best_match_title = search_data['query']['search'][0]['title']
      print(f"Best match found: {best_match_title}")
    else:
      print("No Wikipedia page found for this destination.")
      return None

    # Step 2: Use the best match title to get the image
    url_image = "https://en.wikipedia.org/w/api.php"
    image_params = {
      'action': 'query',
      'prop': 'pageimages',
      'titles': best_match_title,
      'format': 'json',
      'pithumbsize': 500,
      'utf8': 1,
    }
    image_response = requests.get(url_image, params=image_params)
    image_response.raise_for_status()
    image_data = image_response.json()

    pages = image_data['query']['pages']
    for page_id, page_data in pages.items():
      if 'thumbnail' in page_data:
        return page_data['thumbnail']['source']

    print("No image found for this page.")
    return None

  except requests.exceptions.RequestException as e:
    print(f"Error occurred: {e}")
    return None


destination = " Lunch at The Fish Factory goa"

# Call the combined function
image_url = get_wikipedia_image_for_specific_destination(destination)

if image_url:
    print(f"Image URL: {image_url}")
else:
    print("No image available for the destination.")

