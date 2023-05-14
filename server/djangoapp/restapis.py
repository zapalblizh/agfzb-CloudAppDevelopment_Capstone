import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

def get_request(url, **kwargs):

    # If argument contains API KEY
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            # Basic authentication GET
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["language"] = "en"
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # no authentication GET
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def post_request(url, payload, **kwargs):
    print("POST to {} ".format(url))
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def get_dealers_from_cf(url, **kwargs):
    results = []

    # Call get_request with a URL parameter
    json_result = get_request(url)
    
    # print("HHHHHHHHHhello world")
    # print(json_result)

    if json_result:
        # print("FFFFFFFFFFFFFFFF Hello World")
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
            # print(dealer_doc)
            # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], 
                                   city=dealer_doc["city"], 
                                   full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], 
                                   lat=dealer_doc["lat"], 
                                   long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], 
                                   zip=dealer_doc["zip"])
            # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
            # print(dealer_obj.city)
            # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

            results.append(dealer_obj)
    # print(results)
    return results

def get_dealer_by_id_from_cf(url, id):
    results = []

    # Call get_request with a URL parameter
    json_result = get_request(url, id=id)

    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]

            if dealer_doc["id"] == id:
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(address=dealer_doc["address"], 
                                       city=dealer_doc["city"], 
                                       full_name=dealer_doc["full_name"],
                                       id=dealer_doc["id"], 
                                       lat=dealer_doc["lat"], 
                                       long=dealer_doc["long"],
                                       short_name=dealer_doc["short_name"],
                                       st=dealer_doc["st"], 
                                       zip=dealer_doc["zip"])                    
                results.append(dealer_obj)

    return results[0]

def get_dealer_reviews_from_cf(url, dealerId):
    results = []

    json_result = get_request(url, dealerId=dealerId)

    if json_result:
        reviews = json_result["body"]["data"]["docs"]

        for dealer_review in reviews:  
            review_obj = DealerReview(dealership=dealer_review["dealership"],
                                      name=dealer_review["name"], 
                                      purchase=dealer_review["purchase"], 
                                      review=dealer_review["review"])

            if 'purchase_date' in dealer_review:
                review_obj.purchase_date = dealer_review['purchase_date']

            if 'car_make' in dealer_review:
                review_obj.car_make = dealer_review['car_make']

            if 'car_model' in dealer_review:
                review_obj.car_model = dealer_review['car_model']

            if 'car_year' in dealer_review:
                review_obj.car_year = dealer_review['car_year']

            if 'id' in dealer_review:
                review_obj.id = dealer_review['id']

            sentiment = analyze_review_sentiments(review_obj.review)
            print(sentiment)
            review_obj.sentiment = sentiment
            results.append(review_obj)

    return results


