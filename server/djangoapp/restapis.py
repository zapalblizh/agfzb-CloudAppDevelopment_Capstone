import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
import time

def get_request(url, **kwargs):

    # If argument contains API KEY
    apikey = kwargs.get("apikey")
    print("GET from {} ".format(url))
    try:
        if apikey:
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

        # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-")
        # print(json_result)
        # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-")

        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:

            # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-")
            # print(dealer)
            # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

            # Get its content in `doc` object
            dealer_doc = dealer

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

def get_dealer_reviews_from_cf(url, id):
    results = []

    json_result = get_request(url, id=id)

    if json_result:

        # print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
        # print(json_result)
        # print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

        reviews = json_result["data"]["docs"]
        
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

def analyze_review_sentiments(dealer_review): 

    apikey = "Uc622BJbYFeCayawPcrKes_nDRPkeAm965lAOcFMtoF-"
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/972d8703-8374-460c-9cc7-960171e3ee5e"

    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)


    response = natural_language_understanding.analyze(
        text=dealer_review,
        language='en',
        features=Features(sentiment=SentimentOptions(targets=[dealer_review]))
    ).get_result()

    print(json.dumps(response, indent=2))

    return response["sentiment"]["document"]["label"]

