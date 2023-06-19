import json
import os
import pathlib
import time
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from zipfile import ZipFile
import shutil
import rasterio
import logging
import traceback

PLANET_API_KEY=settings.PLANET_API_KEY 
authVar = HTTPBasicAuth(PLANET_API_KEY, '')
#https://developers.planet.com/apis/orders/reference/#tag/Orders/operation/createOrder
#Cancel an order
#PUT: https://api.planet.com/compute/ops/orders/v2/{order_id}

def cancelOrder(orderID):
    auth = HTTPBasicAuth(PLANET_API_KEY, '')
    headers = {'content-type': 'application/json'}
    response = requests.put('https://api.planet.com/compute/ops/orders/v2/'+orderID, auth=authVar, headers=headers)
    print(response.json())
    
    return response


def placePlanetOrder(orderName, geometrycoordinates, fromDate, toDate):

    
    # API Key stored as an env variable
   

    orders_url = 'https://api.planet.com/compute/ops/orders/v2'
    data_url = "https://api.planet.com/data/v1"
    #requests.get('https://api.planet.com/compute/ops/orders/v2/69d79258-e91c-4684-a4d1-6d8654860dce', auth= HTTPBasicAuth(PLANET_API_KEY, '')).json()['state']


    
    response = requests.get(data_url, auth=authVar)

    #https://geojson.io/
    #1st co-ordinates


    order_name = orderName
    geometry = {
        "type":"Polygon",
        "coordinates":geometrycoordinates    
    }




    geometry_filter = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": geometry
    }

    # get images acquired within a date range
    date_range_filter = {
    "type": "DateRangeFilter",
    "field_name": "acquired",
    "config": {
        "gte":fromDate,
        "lte":toDate
    }
    }

    # only get images which have <50% cloud coverage
    cloud_cover_filter = {
    "type": "RangeFilter",
    "field_name": "cloud_cover",
    "config": {
        "lte": 0.5 #0.7
    }
    }

    instrument_filter = {
    "type":"StringInFilter",
    "field_name": "instrument",
    "config": ["PSB.SD"]
    }


    # combine our geo, date, cloud filters
    combined_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_range_filter, cloud_cover_filter, instrument_filter]
    }


    item_type = "PSScene"

    # API request object
    search_request = {
    "item_types": [item_type], 
    "filter": combined_filter
    }

    # fire off the POST request
    search_result = requests.post('https://api.planet.com/data/v1/quick-search', auth=HTTPBasicAuth(PLANET_API_KEY, ''), json=search_request)
    # print(search_result.json(),"search_result")
    image_idss = [feature['id'] for feature in search_result.json()['features']]
    

    # extract image IDs only


    def image_footprint(item_id, item_type="PSScene"):
        auth = HTTPBasicAuth(PLANET_API_KEY, '')
        url = f"https://api.planet.com/data/v1/item-types/{item_type}/items/{item_id}"
        
        response = requests.get(url, auth=authVar)
        coords = response.json()["geometry"]["coordinates"]
        
        polygons = [Polygon(geom) for geom in coords]
        gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=polygons)
        
        return gdf


    def calc_overlap(geometry, image_id, item_type="PSScene"):
        # read scene footprint as geodataframe
        scene_footprint = image_footprint(image_id, item_type="PSScene")

        # convert search-geometry into a geodataframe
        polygons = [Polygon(geom) for geom in geometry["coordinates"]]
        gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=polygons)

        # calculate the intersection between scene footprint and original geometry
        intersection = gpd.overlay(gdf, scene_footprint, how='intersection')

        # divide by original geometry area to see % overlap
        intersection_area = intersection.area.sum()
        area_queried = gdf.area.sum()
        pct_overlap = 100* (intersection_area / area_queried)
        
        return pct_overlap

    



    if image_idss:
        image_ids = [im_id for im_id in image_idss if calc_overlap(geometry, im_id) > 95]
        #print(image_ids)
        if image_ids:
            auth = HTTPBasicAuth(PLANET_API_KEY, '')
            # response = requests.get(orders_url, auth=authVar)

            # orders = response.json()['orders']
            headers = {'content-type': 'application/json'}
            #analytic_8b_udm2 #analytic_5b_udm2 #ortho_analytic_8b_sr #visulas

            single_product = [
                {
                "item_ids": [image_ids[0]],
                "item_type": "PSScene",
                "product_bundle": "analytic_8b_sr_udm2" 
                }
            ]

            multi_src_products = [
                {
                "item_ids": [image_ids],
                "item_type": "PSScene",
                "product_bundle": "analytic_8b_sr_udm2"
                },
                {
                "item_ids": [image_ids[0]],
                "item_type": "PSScene",
                "product_bundle": "analytic_sr_udm2"
                },
            ]

            bandmath = {
            "bandmath": {
                "b1": "b1", # Coastal Blue
                "b2": "b2", # Blue
                "b3": "b3", # Green I
                "b4": "b4", # Green   
                "b5": "b5", # Yellow
                "b6": "b6", # Red
                "b7": "b7", # Red Edge
                "b8": "b8", # Near-infrared
                "b9": "(b8 - b6) / (b8 + b6)", #NDVI  (b8-b6)/(b8+b6)
                "pixel_type": "32R",
            }
            }


            harmonize = {
                "harmonize": {
                    "target_sensor": "Sentinel-2"
                }
            }



            request = {
            'name': order_name,
            'products': single_product,
            'tools': [{'clip': {'aoi': geometry} }, bandmath, harmonize ],
            "delivery": {
            "single_archive": True,
            "archive_type": "zip"
            #"azure_blob_storage": settings.BLOB_STORAGE
        }
    }

            

            def place_order(request, auth):
                #print(request)
                response = requests.post(orders_url, data=json.dumps(request), auth=authVar, headers=headers)
                #print(response.json())
                order_id = response.json()['id']
                order_url = orders_url + '/' + order_id
                return order_url
                
            tool_order_url = place_order(request, auth)
            state = requests.get(tool_order_url, auth=authVar).json()['state']
            
            return {"flag": True, "message": "success",
            'image_ids':image_ids,'order_id':tool_order_url.split("/")[-1], 
            'order_url':tool_order_url, "order_status": state  }

            # def poll_for_success(tool_order_url, auth, num_loops=100):
            #     count = 0
            #     while(count < num_loops):
            #         count += 1
            #         r = requests.get(tool_order_url, auth=authVar)
            #         response = r.json()
            #         state = response['state']
            #         print(state)
            #         end_states = ['success', 'failed', 'partial']
            #         if state in end_states:
            #             break
            #         time.sleep(20)
                    
            # poll_for_success(tool_order_url, auth)



            # def download_results(results, overwrite=False):
            #     results_urls = [r['location'] for r in results]
            #     results_names = [r['name'] for r in results]
            #     print('{} items to download'.format(len(results_urls)))
                
            #     for url, name in zip(results_urls, results_names):
            #         path = pathlib.Path(os.path.join(order_name, name))
                    
            #         if overwrite or not path.exists():
            #             print('downloading {} to {}'.format(name, path))
            #             r = requests.get(url, allow_redirects=True)
            #             path.parent.mkdir(parents=True, exist_ok=True)
            #             open(path, 'wb').write(r.content)
            #         else:
            #             print('{} already exists, skipping {}'.format(path, name))
                        

            # #f02d4614-4811-4cbf-9ea4-b76c6afcb0de
            # r = requests.get(tool_order_url, auth=authVar)
            # response = r.json()
            # results = response['_links']['results']
            
            # download_results(results)
        else:
            return {"flag": False, "order_status": "No (100%) images", "image_ids":[] }

    else:
        return {"flag": False, "order_status": "No images", "image_ids":[] }

def upload_blob(fileName, file, mime_type, flag=1):
               
    cnt_settings = ContentSettings(content_type=mime_type)
    blob_service_client = BlobServiceClient.from_connection_string(settings.BLOB_STORAGE_STRING)
    container_client = blob_service_client.get_container_client(settings.BLOB_STORAGE_CONTAINER)
    blob_client = container_client.get_blob_client(fileName)

    if flag == 1:
        with open(file,'rb') as data:
            blob_client.upload_blob(data,overwrite=True, content_settings=cnt_settings)
    else:
        # Open the dataset
        blob_client.upload_blob(file, overwrite=True, content_settings=cnt_settings)

    if blob_client.url:
        
        return blob_client.url


def download_zip_results(results, pathDir,order_id,overwrite=False):
    """
    Download Planet imagery
    """
    logger = logging.getLogger('flask')
    results_urls = [r['location'] for r in results['_links']['results']]
    results_names = [r['name'] for r in results['_links']['results']]
    #print('{} items to download'.format(len(results_urls)))
    paths=[]

    for url, name in zip(results_urls, results_names):
        path = pathlib.Path(os.path.join(pathDir, 'PlanetDownloads', name))

        paths.append(path)

        if overwrite or not path.exists():
            #print('downloading {} to {}'.format(name, path))
            r = requests.get(url, allow_redirects=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'wb') as file:
                file.write(r.content)
            
            
        else:
            print('{} already exists, skipping {}'.format(path, name))

    zip_files = [x.__str__() for x in paths if x.suffix == ".zip" ]    
    logger.info(('zip_files Info{0} '). format(zip_files))
    path_list = zip_files[0].split(os.sep)
    print(path_list, "path_list")
    blobZipUrl = upload_blob(path_list[-2]+"_"+path_list[-1], zip_files[0], "application/x-zip-compressed")    
    
    logger.info(('blobZipUrl Info{0} '). format(blobZipUrl))
    unzipped_data_directory = pathlib.Path(os.path.join(pathDir, 'unzipped_data'))#"/arcgis/home/unzipped_data"
    zipfile_ob = ZipFile(zip_files[0])
    file_names = zipfile_ob.namelist()
    zipfile_ob.extractall(path=unzipped_data_directory)
    
    tiff_paths = [r for r in file_names if '_SR_' in r]
    logger.info(('tiff_paths Info{0} '). format(tiff_paths))
    # with zipfile_ob.open(tiff_paths[0]) as tiff_file:
    #     blobUrl = upload_blob(tiff_paths[0].split("/")[1], tiff_file, "image/tiff", flag=2)

    # unzipped_data_directory = pathlib.Path(os.path.join(pathDir, 'unzipped_data'))#"/arcgis/home/unzipped_data"
    # for zip_file in zip_files:
    #     z = ZipFile(zip_file)
    #     z.extractall(path=unzipped_data_directory)
    
    filePath = os.path.join(pathDir, 'unzipped_data', 'files', tiff_paths[0].split("/")[1])
    
    with rasterio.open(filePath, "r+") as src:
        src.nodata = 0
        src.close()
    
    with open(filePath, 'rb') as file:
        blobUrl = upload_blob(order_id+"_"+tiff_paths[0].split("/")[1], file, "image/tiff", flag=2)
    
    #Start NDVI
    with rasterio.open(filePath) as src:
        red_band = src.read(6)
        nir_band = src.read(8)
        profile = src.profile
    


    np.seterr(divide='ignore', invalid='ignore')
    # Calculate the NDVI using the formula
    ndvi = (nir_band - red_band) / (nir_band + red_band)

    # Set negative values of NDVI to 0
    #ndvi[ndvi < 0] = 0

    # Create a new raster image to save the NDVI data

    profile.update(dtype=rasterio.float32, count=1, nodata=0)
    outputFilename = tiff_paths[0].split("/")[1]
    ndviFilename = outputFilename.split(".")[0]+"_ndvi."+outputFilename.split(".")[1]
    ndvifilePath = os.path.join(pathDir, 'unzipped_data', 'files', ndviFilename)
    
    with rasterio.open(ndvifilePath, 'w', **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)

    with open(ndvifilePath, 'rb') as file:
        blobNDVIUrl = upload_blob(order_id+"_"+ndviFilename, file, "image/tiff", flag=2)
    #End NDVI
    return({"blobZipUrl":blobZipUrl, "blobImageUrl":blobUrl, 'blobNDVIUrl':blobNDVIUrl})

def validate_order(order_json):
    """
    Validate that an order is completed and available for download
    """
    #check if the order has been successfully completed, if not, exit the function
    if order_json['state'] != 'success':
        print("Order isn't completed yet")
        return False
    
    #also check that this is 8 band PlanetScope imagery
    if order_json["products"][0]["product_bundle"] != "analytic_8b_sr_udm2":
        print("Order is not 8 band PlanetScope Imagery")
        return False

    return True

def orderUpload(order_id):
    logger = logging.getLogger('flask')
    try:
        download_paths = {}
        order_json = requests.get('https://api.planet.com/compute/ops/orders/v2/'+str(order_id), auth=authVar).json()
        #print(order_json)
        #print(order_json['state'])
        logger.info('*************orderUpload ******************')
        logger.info(('orderUpload Info json{0} '). format(order_json))
        if order_json['state'] == 'queued' or order_json['state'] == 'running' :
            return {'status':2, "order_json":order_json, 'order_status': order_json['state']}
        elif order_json['state'] == 'failed':
            return {"blobPaths":download_paths, "order_json":order_json, 'order_status': order_json['state'], 'status':4}
        else:
            dirName = 'home'
            if validate_order(order_json) is True:
                #if there are zips, unzip and extract
                #then return the tiff file paths
                zip_archives = [r['location'] for r in order_json['_links']['results']
                        if r['name'].endswith(".zip")]
                if len(zip_archives)>0:
                    logger.info('*************download_zip_results start ******************')
                    download_paths = download_zip_results(order_json, dirName, order_id)
                    shutil.rmtree(os.path.join(dirName))
                    
                else:
                    
                    tiff_paths = [[r['location'],r['name']] for r in order_json['_links']['results'] if '_SR_' in r['name']]
                    path = pathlib.Path(os.path.join(dirName, 'PlanetDownloads', tiff_paths[0][1]))
                    r = requests.get(tiff_paths[0][0], allow_redirects=True)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(path, 'wb') as file:
                        file.write(r.content)

                    with rasterio.open(path, "r+") as src:

                        # Update the NoData value
                        src.nodata = 0
                        src.close()
                    
                    
                    with open(path, 'rb') as file:                    
                        blobUrl = upload_blob(order_id+"_"+tiff_paths[0][1].split("/")[-1], file, "image/tiff", flag=2)

                    #Start NDVI Image 
                    with rasterio.open(path) as src:
                        red_band = src.read(6)
                        nir_band = src.read(8)
                        profile = src.profile
                    


                    np.seterr(divide='ignore', invalid='ignore')
                    # Calculate the NDVI using the formula
                    ndvi = (nir_band - red_band) / (nir_band + red_band)

                    # Set negative values of NDVI to 0
                    #ndvi[ndvi < 0] = 0

                    # Create a new raster image to save the NDVI data

                    profile.update(dtype=rasterio.float32, count=1, nodata=0)
                    outputFilename = tiff_paths[0][1].split("/")[-1]
                    #print(outputFilename)
                    ndviFilename = outputFilename.split(".")[0]+"_ndvi."+outputFilename.split(".")[1]
                    ndvifilePath = pathlib.Path(os.path.join(dirName, 'PlanetDownloads', ndviFilename))
                    
                    with rasterio.open(ndvifilePath, 'w', **profile) as dst:
                        dst.write(ndvi.astype(rasterio.float32), 1)

                    with open(ndvifilePath, 'rb') as file:
                        blobNDVIUrl = upload_blob(order_id+"_"+ndviFilename, file, "image/tiff", flag=2)

                    #End NDVI Image 
                        
                    download_paths= {"blobImageUrl":blobUrl, 'blobNDVIUrl':blobNDVIUrl}
                    shutil.rmtree(os.path.join(dirName))
                
            

                return {'status':3,"blobPaths":download_paths, "order_json":order_json, 'order_status': order_json['state']}
        
    
    except Exception as e:
        print(e, "exception")
        import inspect
        logger.info(('orderUpload exception Info{0} '). format(str(e)))
        logger.info("Exception raised in %s" % inspect.trace())
        logger.info("Exception raised in method %s" % inspect.trace()[-1][3])
        
    
    
    



