from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential
from typing import List, Dict
from fuzzywuzzy import process

class AzureImageHandler:
    
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)

    def list_publishers(self, location: str ='eastus') -> List[str]:
        publishers = []
        try:
            for publisher in self.compute_client.virtual_machine_images.list_publishers(location):
                publishers.append(publisher.name)
        except Exception as e:
            print(f"Error fetching publishers: {e}")
        return publishers

    def list_offers(self, location: str, publisher_name: str) -> List[str]:
        offers = []
        try:
            for offer in self.compute_client.virtual_machine_images.list_offers(location, publisher_name):
                offers.append(offer.name)
        except Exception as e:
            print(f"Error fetching offers: {e}")
        return offers

    def list_available_images(self, location: str ='eastus') -> Dict[str, str]:
        # List publishers
        # publishers = self.list_publishers(location)
        # print("\nAvailable publishers:")
        # for i, publisher in enumerate(publishers, 1):
        #     print(f"{i}. {publisher}")

        # publisher_choice = int(input("\nSelect a publisher by number: "))
        # chosen_publisher = publishers[publisher_choice-1]

      # List publishers
        publishers = self.list_publishers(location)
        print("\nAvailable publishers:")
        for i, publisher in enumerate(publishers, 1):
            print(f"{i}. {publisher}")

        publisher_input = input("\nType a publisher name (or part of it): ").lower()

        # First, check for exact prefix matches
        startswith_matches = [pub for pub in publishers if pub.lower().startswith(publisher_input)]

        chosen_publisher = None
        if startswith_matches:
            print("\nExact prefix matches:")
            for i, match in enumerate(startswith_matches, 1):
                print(f"{i}. {match}")
            prefix_choice = int(input("\nSelect a publisher by number from the exact prefix matches, or enter 0 to see fuzzy matches: "))
            
            if prefix_choice > 0 and prefix_choice <= len(startswith_matches):
                chosen_publisher = startswith_matches[prefix_choice-1]

        # If no valid prefix choice is made, show fuzzy matches
        if not chosen_publisher:
            matches = process.extract(publisher_input, publishers, limit=15)
            print("\nTop fuzzy matches:")
            for i, (match, score) in enumerate(matches, 1):
                print(f"{i}. {match} (Score: {score})")
            fuzzy_choice = int(input("\nSelect a publisher by number from the fuzzy matches: "))
            
            if fuzzy_choice > 0 and fuzzy_choice <= len(matches):
                chosen_publisher = matches[fuzzy_choice-1][0]

        if not chosen_publisher:
            print("No matching publisher found.")
            return

        # List offers for chosen publisher
        offers = self.list_offers(location, chosen_publisher)
        print("\nAvailable offers for chosen publisher:")
        for i, offer in enumerate(offers, 1):
            print(f"{i}. {offer}")

        offer_choice = int(input("\nSelect an offer by number: "))
        chosen_offer = offers[offer_choice-1]

        try:
        # List SKUs for the chosen publisher and offer
            skus = self.compute_client.virtual_machine_images.list_skus(location, chosen_publisher, chosen_offer)
            
            print("\nAvailable SKUs for chosen publisher and offer:")
            for i, sku in enumerate(skus, 1):
                print(f"{i}. {sku.name}")

            sku_choice = int(input("\nSelect a SKU by number: "))
            chosen_sku = skus[sku_choice-1].name

            # Now, for the chosen SKU, list available images (Optional, as it might be many results. You can skip this part if not needed)
            images = self.compute_client.virtual_machine_images.list(location, chosen_publisher, chosen_offer, chosen_sku)
            for image in images:
                print(f"\nImage ID: {image.id}, Version: {image.name}")

        except Exception as e:
            print(f"An error occurred: {e}")

        return {'publisher': chosen_publisher, 'offer': chosen_offer, 'sku': chosen_sku}


# Test or Usage:
# subscription_id = load_env()
# handler = AzureImageHandler(subscription_id)
# handler.list_available_images()

