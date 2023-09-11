Azure Automation with Python SDK and Terraform

This repository provides a collection of Python scripts aimed at automating various workflows in Microsoft Azure using the Azure SDK for Python. Whether you're looking to manage virtual machines, storage accounts, or any other Azure resource, these scripts serve as practical examples to get you started.
Prerequisites

    Python 3.x
    Azure SDK for Python
    An active Azure subscription

Getting Started

    Clone the Repository

    bash

git clone https://github.com/RWayne93/azure-automation.git
cd azure-automation-python-sdk

Install Dependencies

bash

    pip install -r requirements.txt

    Setup Azure Authentication

    Most scripts in this repository use the DefaultAzureCredential class for authentication. 
    
    Ensure you've set up authentication properly. You can learn more about Azure SDK authentication here. 
    
    https://learn.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id

Contributing

Contributions are welcome! If you have a script or a workflow that can benefit others, feel free to raise a pull request.

    Fork the repository.
    Create your feature branch (git checkout -b feature/YourFeature).
    Commit your changes (git commit -m 'Add some feature').
    Push to the branch (git push origin feature/YourFeature).
    Open a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

    Azure SDK for Python Documentation
