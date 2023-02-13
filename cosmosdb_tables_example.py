# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
# ------------------------------------------------------------

from azure.data.tables import TableServiceClient
from azure.data.tables import TableEntity
from azure.core.pipeline.transport import RequestsTransport
from test_proxy_transport import TestProxyTransport, TestProxyVariables, TestProxyMethods
import os
from dotenv import load_dotenv, find_dotenv

class CosmosDBTablesTestProxy():
    def __init__(self):
        load_dotenv(find_dotenv())
        self.conn_str = os.environ['COSMOS_CONNECTION_STRING']
        self.table_name = 'adventureworks'

    def add_and_get_item(self, table_client):
        # Create new item using composite key constructor
        pro1 = TableEntity(
            RowKey = "68719518388",
            PartitionKey = "gear-surf-surfboards",
            Name = "Ocean Surfboard",
            Quantity = 8,
            Sale = True
        )       

        # Add new item to server-side table
        table_client.create_entity(pro1)

        # Read a single item from container
        product = table_client.get_entity(
            row_key = "68719518388",
            partition_key = "gear-surf-surfboards"
        )
        
        print('Single product:')
        print(product.get('Name'))

    # Read multiple items from container
    def add_and_get_mutiple_items(self, table_client):
        pro2 = TableEntity(
            RowKey = "68719518390",
            PartitionKey = "gear-surf-surfboards",
            Name = "Sand Surfboard",
            Quantity = 5,
            Sale = False
        )

        table_client.create_entity(pro2)

        query_filter = "PartitionKey eq 'gear-surf-surfboards'"
        products = table_client.query_entities(query_filter)

        print('Multiple products:')
        for item in products:
            print(item.get('Name'))
                
    def main(self):
        tpv = TestProxyVariables()
        rs = tpv.session()
        tpm = TestProxyMethods(rs)
        use_proxy = os.environ['USE_PROXY']
        transport = None

        # Override the http transport when using the test proxy.
        # If not using the proxy, the default client http transport will be used.
        if (use_proxy == "true"):
            tpm.host = os.environ['PROXY_HOST']
            tpm.port = os.environ['PROXY_PORT']
            tpm.mode = os.environ['PROXY_MODE']
            tpm.start_test_proxy()
            transport = TestProxyTransport(RequestsTransport(session=rs), tpm.host, tpm.port, tpm.recording_id, tpm.mode)

        #=========================================================================================
        # End of test proxy prologue. Original test code starts here. Everything after this point 
        # represents an app interacting with the Azure Table Storage service.                     
        #=========================================================================================
        
        table_service_client = TableServiceClient.from_connection_string(conn_str=self.conn_str, transport=transport)
        # New instance of TableClient class referencing the server-side table
        table_client = table_service_client.create_table_if_not_exists(table_name=self.table_name)
        self.add_and_get_item(table_client)
        self.add_and_get_mutiple_items(table_client)
        table_client.delete_table()

        #=============================================================================
        # Test proxy epilogue - necessary to stop the test proxy. Note that if you do 
        # not stop the test proxy after recording, your recording WILL NOT be saved!  
        #=============================================================================

        if (use_proxy == "true"):
                tpm.stop_test_proxy()
            
        rs.close()

if __name__ == "__main__":
    ctp = CosmosDBTablesTestProxy()
    ctp.main()