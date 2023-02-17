This project is a Python demo that pairs with an [Azure
SDK blog post](https://aka.ms/azsdk/test-proxy) about reducing cloud testing costs.
=

Testing is a crucial step in the software development process, including software deployed to the cloud. Testing software against a live cloud service like Azure can be costly, since services must be provisioned and maintained in order to run the tests.

The Azure SDK team has developed a lightweight test proxy that allows us to record app interactions with Azure and play them back on demand, significantly reducing our testing costs. We’re now excited to share this tool with the broader Azure development community and invite you to try it out for yourself.

This repository contains a sample project that demonstrates integration
of the record and playback test proxy with an app that interacts with
the Azure Cosmos DB Table Storage service using one of our Python SDKs.

### Prerequisites

The following prerequisites are required to use this application. Please ensure that you have them all installed locally.

- [Python (3.8+)](https://www.python.org/downloads/)
- [Visual Studio Code](https://code.visualstudio.com/Download)
- [Install .NET 6.0 or higher](https://dotnet.microsoft.com/download)
- [Install the test-proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy#installation)

```
dotnet tool update azure.sdk.tools.testproxy --global --add-source https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-net/nuget/v3/index.json --version "1.0.0-dev*"
```

Notes: After installing the tool, run it in a terminal or cmd window by typing the command 'test-proxy'.

### Build and Run the sample

1.Clone the repository.

```
git clone https://github.com/Azure-Samples/record-playback-test-proxy-demo-python.git
cd record-playback-test-proxy-demo-python
```

2.Install the package for this project.

```
pip install -r requirements.txt
```

3.Before running the project, ensure that the following environment variables are set in .env file:

- COSMOS_CONNECTION_STRING
- USE_PROXY
- PROXY_HOST
- PROXY_PORT
- PROXY_MODE

4.Run the sample.

```
python cosmosdb_tables_example.py
```

The included recording file is provided for illustration purposes only, it can't be used to play back the test since the resources associated with it no longer exist in Azure.

The test proxy is compatible with all four major languages and can be
easily installed using the standard dotnet tool installation process as
described in the blog post. To use it, you\'ll need to be able to reroute
your app requests to the test proxy via modifications to the request
headers.
