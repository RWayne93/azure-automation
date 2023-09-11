import os

def load_env(filename='.env'):
    with open(filename) as f:
        for line in f:
            if line.strip():
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    return os.getenv('AZURE_SUBSCRIPTION_ID')

#load_env()

#print(os.getenv('AZURE_SUBSCRIPTION_ID'))