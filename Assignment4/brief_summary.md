# Azure Data Factory End-to-End Data Pipeline

## Objective

To understand Azure cloud services and build an end-to-end data pipeline using Azure Blob Storage and Azure Data Factory (ADF).

## Implementation

* Created an Azure Resource Group to organize resources.
* Created an Azure Storage Account with source and destination Blob containers.
* Uploaded a CSV file to the source container.
* Created an Azure Data Factory instance and explored Author, Monitor, and Manage sections.
* Configured Linked Services to connect ADF with Azure Blob Storage.
* Created source and destination datasets.
* Added a **Get Metadata** activity to validate file existence and retrieve file properties.
* Added a **Copy Data** activity to transfer data from the source container to the destination container.
* Configured IAM permissions to enable secure access between Azure Data Factory and Azure Storage.
* Executed the pipeline using Debug/Trigger and monitored execution through ADF Monitor.

## Results

* Successfully validated source file metadata.
* Successfully copied the CSV file from the source container to the destination container.
* Verified pipeline execution status and activity logs.
* Confirmed the output file was created in the destination location.

## Conclusion

This project demonstrated the creation of a complete data ingestion and movement pipeline using Azure services. Azure Data Factory was used to orchestrate metadata validation and data transfer operations, while Azure Blob Storage served as the source and destination storage layer. The successful execution of the pipeline validated the end-to-end workflow.
