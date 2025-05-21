import asyncio
import json
import requests
import uuid
from services.database import get_all_products


meili_url = 'https://meilisearch.dealwallet.com/'   
api_key = 'diNupMWTaJtR1pluZfoNzA=='             
index_name = 'products_summarization'  

async def index_product(products):
    try:
        
        create_index_url = f"{meili_url}/indexes"
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.post(create_index_url, json={"uid": index_name}, headers=headers)

        if response.status_code == 201:
            print(f"Index '{index_name}' created successfully.")
        else:
            print(f"Error creating index: {response.text}")

        add_documents_url = f"{meili_url}/indexes/{index_name}/documents"
        response = requests.post(add_documents_url, json=products, headers=headers)
        print(response.text)
        # Check if the documents were added successfully
        if response.status_code == 202:
            print("Documents added successfully.")
        else:
            print(f"Error adding documents: {response.text}")


    except Exception as e:
        print(f"Error indexing product {product['id']}: {e}")

async def main():
    products = await get_all_products()
    print(f"Total products: {len(products)}") 
    final_products = []
    if products:
        for product in products:
            if product['summarization']:
                product['price'] = product['price'].replace("₹", '')
                product['original_price'] = product['original_price'].replace("₹", '')
                del product['org_id']
                del product['branch_id']
                del product['categorie_id']
                final_products.append(product)
        print(f"Total products to index: {len(final_products)}")    
        await index_product(final_products)

asyncio.run(main())