from response_writer import *
from acquire_request import *
import logging
import os

logger = logging.getLogger()
logging.basicConfig(level=os.environ.get("LOGLEVEL"))


def validate_request(req):

    # check the folder exists, i.e. the product
    try:
        logging.debug(f'req product id: {req.product_id}')
        logging.debug(f'req csp id: {req.csp_id}')
        with open("./catalogue/" + req.ds_id + ".json",'r', encoding='ISO-8859-1') as catalogue_load:
            catalogue_file = catalogue_load.read()
        catalogue = json.loads(catalogue_file)
        #logger.info(catalogue)
        for element in catalogue['cspDisclosureCatalogue']['cspDisclosureProduct']:

            #for value in ['cspDisclosureCatalogue']['cspDisclosureProduct'][0]:
            for attribute, value in element.items():
                if attribute == "cspDisclosureProductID":
                    #logger.info(value)
                    if value.replace(':',"") == req.product_id:
                        logger.info("Doing specific validation checks for DataRetain")
                        if productOutputsAreValid(req.initial_req,req.product_id,element) == False:
                            return write_error_response(400, "Invalid cspOutputDataTypeID", "THIS IS AN ERROR YOU WILL GET IF INCOMPATIBLE WITH DATARETAIN, CONTACT NCDS")
                        if productFormatsAreValid(req.initial_req,req.product_id,element) == False:
                            return write_error_response(400, "Invalid optionalResultFormatID", "THIS IS AN ERROR YOU WILL GET IF INCOMPATIBLE WITH DATARETAIN, CONTACT NCDS")
        result_folder = "./result_files/{}/{}".format(req.csp_id,req.product_id)
        logger.info(result_folder)
        #for f in os.scandir(result_folder):
            #logger.info(f.path)

        store_request(req)

    except FileNotFoundError as e:
        logger.info("requested product does not exist")
        #return write_error_response(400, "Invalid Product ID", "Unable to find a Disclosure Product with the specified ID: {}".format(req.product_id))
        return False
    except AttributeError as e:
        logger.info("requested product does not exist")
        #return write_error_response(400, "Invalid Product ID", "Unable to find a Disclosure Product with the specified ID: {}".format(req.product_id))
        return False
    finally:
        store_request(req)

    return True

def new_request_handler(body,path):
    # TODO check schema

    # Have learnt there is no python Schema validator
    # will need to be manually implemented against a specific schema version
    try:
        req = AcquireRequest(path, body)
        logger.info(req.to_string)
        return req
    except AssertionError as inv:
        logger.info("Request was invalid")
        return write_error_response(400, "Invalid Request", "Schema validation failed: {}".format(inv.args[0]))

#This code is here to mimic data retain
def productOutputsAreValid(req,productId,productSchema):
    cspOutputDataTypeName = []
    for element in productSchema['productOutput']:
        logger.info("Element productOutput")
        logger.info(element)
        if not element['optional']:
            cspOutputDataTypeName.append(element["cspOutputDataTypeID"])

    logger.info("cspOutputDataTypeName")
    logger.info(cspOutputDataTypeName)
    jsonReq = json.loads(req)
    if "cdOptionalOutput" in jsonReq['cdAcquisitionRequest']['cdRequestDetails']:
        for outputElement in jsonReq['cdAcquisitionRequest']['cdRequestDetails']['cdOptionalOutput']:
            logger.info("OutputElement")
            logger.info(outputElement)
            if outputElement['cspOutputDataTypeID'] in cspOutputDataTypeName:
                logger.info("Request is NOT compatible with DataRetain")
                return False
    logger.info("Request is compatible with DataRetain")
    return True

#This code is here to mimic data retain
def productFormatsAreValid(req,productId,productSchema):
    cspFormatTypeName = []
    for element in productSchema['supportedResultFormat']:
        logger.info("Element supportedResultFormat")
        logger.info(element)
        if not element['optional']:
            cspFormatTypeName.append(element["resultFormatID"])

    logger.info("cspFormatTypeName")
    logger.info(cspFormatTypeName)
    jsonReq = json.loads(req)
    for outputElement in jsonReq['cdAcquisitionRequest']['cdRequestDetails']['optionalResultFormatID']:
        logger.info("optionalResultFormatID")
        logger.info(outputElement)
        if outputElement in cspFormatTypeName:
            logger.info("Request is NOT compatible with DataRetain")
            return False
    logger.info("Request is compatible with DataRetain")
    return True
